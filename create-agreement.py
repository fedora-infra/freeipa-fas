#!/usr/bin/env python3

from argparse import ArgumentParser
from subprocess import run


def run_cmd(cmd, **kwargs):
    print(" ".join(cmd))
    run(cmd, check=True, **kwargs)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("name", metavar="NAME", help="agreement name")
    parser.add_argument("--desc", help="agreement text")
    return parser.parse_args()


def main():
    args = parse_args()
    agreement_name = args.name
    cmd = ["ipa", "fasagreement-add", agreement_name]
    if args.desc:
        cmd.extend(["--desc", args.desc])
    # Create the agreement
    run_cmd(cmd)
    # Create the corresponding group
    group_name = f"signed_{agreement_name}"
    run_cmd(
        [
            "ipa",
            "group-add",
            group_name,
            "--desc",
            f"Signers of the {agreement_name}",
        ]
    )
    # Add the automember rule
    run_cmd(["ipa", "automember-add", "--type", "group", group_name])
    run_cmd(
        [
            "ipa",
            "automember-add-condition",
            "--type=group",
            "--key=memberof",
            "--inclusive-regex",
            f"^cn={agreement_name},cn=fasagreements,",
            group_name,
        ]
    )


if __name__ == "__main__":
    main()
