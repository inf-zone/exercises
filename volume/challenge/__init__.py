import struct

import check50
import check50.c

# Samples that a factor of 2 or 3 pushes past what an int16_t holds.
SAMPLES = [1000, 20000, -20000, 32767, -32768, -1]


@check50.check()
def exists():
    """volume.c exists"""
    check50.exists("volume.c")

    write_wav("input.wav", SAMPLES)


@check50.check(exists)
def compiles():
    """volume.c compiles"""
    check50.c.compile("volume.c", lcs50=True)


@check50.check(compiles)
def clips_double():
    """clips samples to the range of an int16_t, factor of 2"""
    check_factor("2", [[2000, 32767, -32768, 32767, -32768, -2]])


@check50.check(compiles)
def clips_triple():
    """clips samples to the range of an int16_t, factor of 3"""
    check_factor("3", [[3000, 32767, -32768, 32767, -32768, -3]])


@check50.check(compiles)
def still_halves():
    """still reduces audio volume, factor of 0.5"""
    # Truncating or rounding the floats to ints are both fine.
    check_factor("0.5", [
        [500, 10000, -10000, 16383, -16384, 0],
        [500, 10000, -10000, 16384, -16384, -1],
        [500, 10000, -10000, 16384, -16384, 0],
        [500, 10000, -10000, 16383, -16384, -1],
    ])


@check50.check(compiles)
def keeps_header():
    """copies the header unchanged"""
    check50.run("./volume input.wav output.wav 2").exit(0)

    with open("input.wav", "rb") as file:
        expected = file.read(44)
    with open("output.wav", "rb") as file:
        actual = file.read(44)

    if actual != expected:
        raise check50.Failure("the first 44 bytes of output.wav differ from input.wav")


def check_factor(factor, accepted):
    check50.run(f"./volume input.wav output.wav {factor}").exit(0)
    samples = read_samples("output.wav")

    if samples not in accepted:
        raise check50.Mismatch(
            " ".join(map(str, accepted[0])),
            " ".join(map(str, samples)),
            help=f"the samples of input.wav are {' '.join(map(str, SAMPLES))}",
        )


def write_wav(name, samples):
    """A mono 16-bit WAV file of *samples*, with the usual 44-byte header."""
    data = struct.pack(f"<{len(samples)}h", *samples)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + len(data), b"WAVE",
        b"fmt ", 16, 1, 1, 44100, 44100 * 2, 2, 16,
        b"data", len(data),
    )

    with open(name, "wb") as file:
        file.write(header + data)


def read_samples(name):
    try:
        with open(name, "rb") as file:
            data = file.read()[44:]
    except FileNotFoundError:
        raise check50.Failure("output.wav was not created")

    if len(data) % 2:
        raise check50.Failure("output.wav does not hold whole 16-bit samples")

    return list(struct.unpack(f"<{len(data) // 2}h", data))
