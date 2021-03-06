#! /usr/bin/python

import argparse

program_description = ("pypes will calculate the specs for a set of equal "
                       "tempered pipes in a chromatic scale starting at a "
                       "given lowest frequency and continuing for a given "
                       "number of steps.  The speed of sound can also be "
                       "specified in meters per second.  The lengths of the "
                       "pipes are given in centimeters.  The user can also "
                       "specify a modality by providing a list of steps as "
                       "well as the index (with 1 being the root) of the "
                       "lowest pipe.")
# gather up the specs
parser = argparse.ArgumentParser(description = program_description);
parser.add_argument("--fundamental", "-f", type = float, 
                    default = 261.6255653005987,
                    help = ("Frequency (in Hz) of the lowest note.  Middle C "
                            "by default (about 261.62 Hz)."))
parser.add_argument("--step", "-s", type = int, default = 12,
                   help = ("The number of chromatic steps per octave.  12 "
                           "by default."))
parser.add_argument("--numpipes", "-n", type = int, default = 13,
                    help = ("The number of pipes to calculate.  13 "
                            "by default."))
parser.add_argument("--velocity", "-v", type = float, default = 343,
                    help = ("The speed of sound in meters per second.  343 "
                            "by default"))
parser.add_argument("--mode", "-m", nargs = '+', type = int, default = None,
                    help = ("Sequence of chromatic steps to make p a scale.  "
                            "(e.g. Ionian major: 2 2 1 2 2 2 1).  Scales "
                            "will be chromatic by default.  These steps "
                            "should sum to the total number of steps per "
                            "scale but and pypes will complain if they don't "
                            "but it will perform the computations anyway."))
parser.add_argument("--diatonic", "-D", action = "store_true",
                    default = False,
                    help = ("Shorthand for mode [2, 2, 1, 2, 2, 2, 1].  "
                            "Explicitly setting a mode with the --mode option "
                            "will override this."))
parser.add_argument("--index", "-i", type = int, default = 1,
                    help = ("Tonal index of the lowest pipe (only useful "
                            "if a mode has been specified).  1 by default."))
parser.add_argument("--round", "-r", type = int, default = 2,
                    help = ("How many digits past the decimal point to round "
                            "the lengths off to."))
parser.add_argument("--plug", "-p", type = float, default = 0.0,
                    help = ("The depth of the plug that will be used to stop "
                            "the tubes.  0 by default"))
parser.add_argument("--diameter", "-d", type = float, default = 0.0,
                    help = ("The diameter of the tubes, for more accurate "
                            "calculations."))
parser.add_argument("--extra", "-x", default = False, 
                    action="store_true",
                    help = ("Show extra information, meaning the frequency "
                            "of each pipe."))
args = parser.parse_args()

def get_length(freq, args):
    """Returns the length in cm of a tube with the desired resonant frequency."""
    velcm = args.velocity * 100.0
    return float(velcm / (4 * freq) + args.plug) - (0.4 * args.diameter)

# futz with the mode a bit
if not args.mode:
    if args.diatonic:
        # diatonic is shorthand for diatonic scale keyed to Maj
        args.mode = [2, 2, 1, 2, 2, 2, 1]
    else:
        # chromatic by default
        args.mode = [1] * args.step
# rotate until first pipe is aligned with correct index
off = args.index - 1
args.mode = args.mode[off:] + args.mode[:off]
# this lets us simplify some computations later on
pipes_per_octave = len(args.mode)
double_safe = True
if sum(args.mode) != args.step:
    double_safe = False
    print ("The steps in your mode doesn't add up to an octave.  These "
           "results might not make sense.")

# build the table of frequencies for the one chromatic octave
et_step = 2 ** (1.0 / args.step)
chrom_freqs = [0] * args.step
chrom_freqs[0] = args.fundamental
for ith in range(1, args.step):
    chrom_freqs[ith] = chrom_freqs[ith - 1] * et_step
        
# build the table of frequencies for all pipes
pipe_freqs = [0] * args.numpipes
cf_index = 0
pipe_freqs[0] = chrom_freqs[0]
double_safe = False
octave = 1
for ith in range(1, args.numpipes):
    if double_safe and ith > pipes_per_octave:
        # if it's a normally repeating  mode and we're past the first octave,
        # just double the values from an octave below
        pipe_freqs[ith] = pipe_freqs[ith - (pipes_per_octave + 1)] * 2
    else:
        # jump the necessary number of chromatic steps to get to the next 
        # base frequency then multiply it by 2 for every octave we've passed
        if (ith % pipes_per_octave) == 0:
            octave *= 2
        mode_index = (ith - 1) % pipes_per_octave
        cf_index += args.mode[mode_index]
        cf_index %= args.step
        pipe_freqs[ith] = chrom_freqs[cf_index] * octave

# now compute and display the length
pipe_lengths = [get_length(freq, args) for freq in pipe_freqs]
ith_mw = len(str(len(pipe_lengths)))
l_max = ""
l_zp = args.round
for ith, length in enumerate(pipe_lengths):
    # we want cm
    length = "{length:.{l_zp}f}".format(length = round(length, l_zp),
                                         l_zp = l_zp)
    if l_max == "":
        # we're processing the lowest .: longest pipe, make its string length
        # the min width for all further strings representing length
        l_max = len(str(length))
    length = length.rjust(l_max, " ")
    freq = "" if not args.extra else (" ({freq:.{l_zp}f})"
                                      ).format(freq = round(pipe_freqs[ith],
                                                            l_zp),
                                               l_zp = l_zp)

    print ("{ith:{ith_mw}}: {length} cm{freq:}"
           ).format(ith_mw = ith_mw,
                    ith = ith, 
                    length = length,
                    freq = freq)

                                                                
