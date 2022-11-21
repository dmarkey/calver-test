import os
import sys
import json
from subprocess import check_output, CalledProcessError
from time import strftime


def attempt_hotfix_release(version, release_branch):
    check_output(
        ["gh", "release", "create", version, "--target", release_branch, "--generate-notes", "-t",
         f"Automated Hotfix Release {version}"])


def attempt_standard_release(release_branch, version_prefix, iterate_minor=True):
    iterator = 0

    while True:
        try:
            version_number = f"{version_prefix}.{iterator}.0"
            check_output(
                ["gh", "release", "create", version_number, "--target", release_branch, "--generate-notes", "-t",
                 f"Automated Release {version_number}"])
        except CalledProcessError:
            if not iterate_minor:
                raise
            else:
                iterator += 1
        else:
            print(f"Successfully released {release_branch} as {version_number}")
            return


def release(pr_number, version_scheme, mainline_branch):
    result = check_output(["gh", "pr", "view", pr_number, "-c", "--json", "baseRefName,comments,labels,mergedAt"])
    result_parsed = json.loads(result)
    if result_parsed['mergedAt'] is None:
        raise Exception(f"PR {pr_number} is not merged.")
    plain_labels = [x['name'] for x in result_parsed['labels']]
    if "skip-release" in plain_labels:
        print("'skip-release' label present, skipping.")
        return
    if result_parsed['baseRefName'] == mainline_branch:
        version_prefix = strftime(version_scheme)
        attempt_standard_release(mainline_branch, version_prefix)
    else:
        if not [x for x in result_parsed['labels'] if x['name'] == "hotfix"]:
            print("Missing hotfix label, assuming this isn't for release")
            return
        hotfix_branch = result_parsed['baseRefName']
        hotfix_version = "".join(hotfix_branch.split("-")[1:])
        print(f"Attempting for branch {result_parsed['baseRefName']}, version {hotfix_version}")
        attempt_hotfix_release(hotfix_version, hotfix_branch)


if __name__ == "__main__":
    _version_scheme = os.environ.get("VERSION_SCHEME", "%Y.%j")
    _mainline_branch = os.environ.get("MAINLINE_BRANCH", "main")
    _pr_number = sys.argv[1]
    release(_pr_number, _version_scheme, _mainline_branch)
