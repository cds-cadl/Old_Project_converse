import record_voice
import argparse

parser = argparse.ArgumentParser(
    # prog='ModuleTest',
    description='Testing argument parser'
)

parser.add_argument(
    '-f', '--filename', type=str,
    help='enter name of file you want to store the recording to (.wav format)'
)
args = parser.parse_args()

file_name = args.filename or 'demo.wav'

print(file_name)
record_voice.record_to_file(file_name)