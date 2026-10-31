"""Makes a GLB exported from Blender fit the game's rig (docs/PLUGINS.md "커스텀 모델"). Blender cannot keep a bone's rest
exactly: a bone pointing down (the feet, the thumbs) comes back turned ~20 degrees, and the importer's other bone
options turn more, while the game's clips need every bone's rest as the rig has it. This puts each bone back on the
rig's rest turn, where it stands in the file (so a body of other proportions stays so), and works out again what depends
on it: the children's places, the skin's bind matrices (the mesh does not move) and a clip's keys (the pose stays).
Nothing else is left that the server would refuse for no reason: material extensions, a clip's other channels.
Only the Python standard library.

  python fix_model.py model.glb out.glb          a character model
  python fix_model.py --emote wave.glb out.glb   an emote: the rig and its one clip, the meshes dropped

It does not make a wrong rig right: a bone missing or renamed, or one under another parent, is an error here too.
"""
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOATS = 5126


def rig():
    for path in (os.path.join(HERE, "rig.json"), os.path.join(HERE, "..", "..", "data", "rig.json")):
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    sys.exit("rig.json not found beside this script")


def q_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def q_inv(q):
    return (-q[0], -q[1], -q[2], q[3])


def q_norm(q):
    n = math.sqrt(sum(x * x for x in q)) or 1.0
    return tuple(x / n for x in q)


def q_rot(q, v):
    p = q_mul(q_mul(q, (v[0], v[1], v[2], 0.0)), q_inv(q))
    return p[:3]


def inverse_bind(q, p):
    """The inverse of the bone's global transform (rotation q at p), as glTF's column-major MAT4."""
    x, y, z, w = q_inv(q)
    m = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0.0,
         2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0.0,
         2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0.0, 0.0, 0.0, 0.0, 1.0]
    t = q_rot(q_inv(q), p)
    m[12], m[13], m[14] = -t[0], -t[1], -t[2]
    return m


def read_glb(path):
    with open(path, "rb") as f:
        b = f.read()
    if b[:4] != b"glTF":
        sys.exit("not a GLB")
    n = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + n])
    at = 20 + n
    return j, bytearray(b[at + 8:]) if at < len(b) else bytearray()


def write_glb(path, j, bin_):
    text = json.dumps(j, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    text += b" " * (-len(text) % 4)
    bin_ = bytes(bin_) + b"\0" * (-len(bin_) % 4)
    if j.get("buffers"):
        j["buffers"][0]["byteLength"] = len(bin_)
        text = json.dumps(j, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        text += b" " * (-len(text) % 4)
    total = 12 + 8 + len(text) + (8 + len(bin_) if bin_ else 0)
    with open(path, "wb") as f:
        f.write(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(text)) + b"JSON" + text)
        if bin_:
            f.write(struct.pack("<I", len(bin_)) + b"BIN\0" + bin_)


def floats_at(j, accessor):
    """Where an accessor of floats is in the binary chunk: [(offset of each element)], its width in floats."""
    a = j["accessors"][accessor]
    v = j["bufferViews"][a["bufferView"]]
    if a.get("componentType") != FLOATS:
        sys.exit("an accessor that is not of floats where floats are needed")
    width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
    step = v.get("byteStride", width * 4)
    start = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return [start + i * step for i in range(a["count"])], width


def main():
    args = sys.argv[1:]
    emote = "--emote" in args
    if emote:
        args.remove("--emote")
    if len(args) != 2:
        sys.exit(__doc__)
    r = rig()
    j, bin_ = read_glb(args[0])
    nodes = j["nodes"]
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent[c] = i
    by_name = {n.get("name"): i for i, n in enumerate(nodes)}
    for b in r["bones"]:
        if b["name"] not in by_name:
            sys.exit("no bone " + b["name"])
        if b["parent"] >= 0 and nodes[parent.get(by_name[b["name"]], -1)].get("name") != r["bones"][b["parent"]]["name"]:
            sys.exit("the bone %s is not under %s" % (b["name"], r["bones"][b["parent"]]["name"]))

    def local(n):
        return (tuple(n.get("rotation", (0.0, 0.0, 0.0, 1.0))), tuple(n.get("translation", (0.0, 0.0, 0.0))))

    def world(i):
        q, p = local(nodes[i])
        if i in parent:
            uq, up = world(parent[i])
            p = tuple(u + v for u, v in zip(up, q_rot(uq, p)))
            q = q_norm(q_mul(uq, q))
        return q, p

    old = {b["name"]: world(by_name[b["name"]]) for b in r["bones"]} # (every bone's turn and place as the file has them)
    above = world(parent[by_name["Hips"]]) if by_name["Hips"] in parent else ((0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0))
    turn = {}
    for b in r["bones"]: # (parents first: the rig lists them so)
        up_turn = turn[r["bones"][b["parent"]]["name"]] if b["parent"] >= 0 else above[0]
        turn[b["name"]] = q_norm(q_mul(up_turn, tuple(b["rot"])))

    for b in r["bones"]:
        n = nodes[by_name[b["name"]]]
        up_name = r["bones"][b["parent"]]["name"] if b["parent"] >= 0 else None
        up_turn, up_place = (turn[up_name], old[up_name][1]) if up_name else above
        gap = tuple(p - u for p, u in zip(old[b["name"]][1], up_place))
        n["translation"] = list(q_rot(q_inv(up_turn), gap))
        n["rotation"] = list(b["rot"])
        n.pop("scale", None)

    for skin in j.get("skins", []):
        at, _ = floats_at(j, skin["inverseBindMatrices"])
        for k, joint in enumerate(skin["joints"]):
            name = nodes[joint].get("name")
            struct.pack_into("<16f", bin_, at[k], *inverse_bind(turn[name], old[name][1]))

    bones = {by_name[b["name"]]: b for b in r["bones"]}
    fix = {b["name"]: q_norm(q_mul(q_inv(turn[b["name"]]), old[b["name"]][0])) for b in r["bones"]} # each bone's old axes in its new
    for anim in j.get("animations", []):
        kept = []
        for c in anim["channels"]:
            node, path = c["target"].get("node"), c["target"].get("path")
            if node not in bones or not (path == "rotation" or path == "translation" and bones[node]["name"] == "Hips"):
                continue
            kept.append(c)
            if path != "rotation":
                continue
            b = bones[node]
            up = fix[r["bones"][b["parent"]]["name"]] if b["parent"] >= 0 else (0.0, 0.0, 0.0, 1.0)
            at, _ = floats_at(j, anim["samplers"][c["sampler"]]["output"])
            for o in at: # the same pose on the new rests: q' = F(parent) q F(bone)^-1
                q = struct.unpack_from("<4f", bin_, o)
                struct.pack_into("<4f", bin_, o, *q_norm(q_mul(q_mul(up, q), q_inv(fix[b["name"]]))))
        anim["channels"] = kept

    for m in j.get("materials", []):
        m.pop("extensions", None)
    j.pop("extensionsUsed", None)
    if emote:
        for k in ("meshes", "skins", "materials", "images", "textures", "samplers"):
            j.pop(k, None)
        for n in nodes:
            n.pop("mesh", None)
            n.pop("skin", None)
    write_glb(args[1], j, bin_)
    print("%s: %d bones on the rig's rest" % (args[1], len(r["bones"])))


if __name__ == "__main__":
    main()
