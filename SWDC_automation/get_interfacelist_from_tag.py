import argparse
from git import Repo
import sys
import shutil
import os


def parse_args():
    parser = argparse.ArgumentParser(description='Create new tags.')
    parser.add_argument('-r', '--repo', help='file path for repository.')
    parser.add_argument('-t', '--tag', help='name of the tag.')
    parser.add_argument('-w', '--ws', help='workspace location.')
    return parser.parse_args()


def init_repo(repo_path):
    """
    Instantiates a Repo and check so its status is ok
    """
    repo = Repo(repo_path)
    assert not repo.bare, "Empty Repositry"
    repo.git.reset('--hard')
    assert not repo.is_dirty(), "Un-tracked files in branch, clean repository"+str(repo.untracked_files)
    return repo


def checkout_tag(repo, tag):
    """
    Checks out a tag in a repo
    """
    tag_list = [tag_id.name for tag_id in repo.tags]
    if tag not in tag_list:
        raise Exception("ERROR: Tag not found: '{}'".format(tag))
    repo.git.checkout(tag)


def compare_list_versions(version_parts, latest_version):
    """
    Compares an interface list version to the latest version found so far, one index at a time
    Returns whether this specific version is the latest version found or not
    """
    comparison_complete = False
    index = 0
    while not comparison_complete:
        if index >= 1000:  # To prevent an infinite loop
            raise Exception('ERROR: Not able to determine latest version of I/F list after 1000 iterations. Do several lists have the same version?')
        # Since list versions can have different amount of numbers, like 2.1 vs 2.1.1,
        # we need to append zeroes so we can compare their indexes without going out of bounds:
        if index >= len(version_parts):
            version_parts.append(0)
        if index >= len(latest_version):
            latest_version.append(0)

        if version_parts[index] > latest_version[index]:  # Newer version found
            this_version_is_latest = True
            comparison_complete = True
        elif version_parts[index] == latest_version[index]:  # Need to check next index also
            this_version_is_latest = False
            comparison_complete = False
        elif version_parts[index] < latest_version[index]:  # Older version found
            this_version_is_latest = False
            comparison_complete = True
        index += 1
    return this_version_is_latest


def get_version_parts(entry):
    """
    Converts the file name into a list of its version numbers.
    This assumes that the version is the last part of the file name and that it is preceeded by an underscore.
    """
    version = entry.split('_')[-1]  # Version and file type of the interface list, example ['4.1.2.xlsx']
    version_parts = version.split('.')[:-1]  # Individual numbers of the version, i.e ['4', '1', '2']
    version_parts = [int(version_parts[x]) for x in range(len(version_parts))]  # [4, 1, 2]
    return version_parts


def copy_file(file, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    shutil.copy(src=file, dst=directory)


def main(repo, tag, ws):
    Repo = init_repo(repo)
    checkout_tag(Repo, tag)

    if 'gep3_bev' in tag.lower():  # Special case for BEV
        project = 'GEP3_BEV'
    else:
        project = tag.split('-')[0]
    latest_version = []
    entries = []
    newest_IF_list = "No_list"  # To prevent a crash if there are no interface lists in the tag
    for file in os.scandir(repo + "\\Projects\\" + project + "\\Config"):
        if 'SPMEMS' in file.name:  # Find only interface lists
            entries.append(file.name)

    for entry in entries:  # Loop through all interface lists to find the latest one
        version_parts = get_version_parts(entry)
        this_version_is_latest = compare_list_versions(version_parts, latest_version)

        # If this entry is the latest interface list found so far, save the whole name of the file:
        if this_version_is_latest:
            latest_version = version_parts
            newest_IF_list = entry
    # Copies the interface list to the workspace of the machine:
    copy_file(ws + "\\pt_pcc\\Projects\\" + project + "\\Config\\" + newest_IF_list, ws + "\\SWDC_files")
    print("Used interface list: Projects\\" + project + "\\Config\\" + newest_IF_list)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
