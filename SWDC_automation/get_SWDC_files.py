import yaml
import argparse
import os
import artifactory as art
import get_interfacelist_from_tag

parser = argparse.ArgumentParser(description='Read build info from yaml.')
parser.add_argument('-yaml', '--yamlfile', type=argparse.FileType('r'),
                    help='yaml file.')
parser.add_argument('-w', '--ws', help='Workspace.')
parser.add_argument('-u', '--user', help='username.')
parser.add_argument('-p', '--password', help='password.')
args = parser.parse_args()

# Get data/info from yaml
yaml_file = yaml.load(args.yamlfile, Loader=yaml.Loader)     # load yaml to a dictionary
tag_name = yaml_file["spm"]
print("Tag name: ", tag_name)
dbc_list = yaml_file["DBC_files"]
print("DBC files: ", dbc_list)

# Access Artifactory and download DBC files
for file in dbc_list:
    path = art.ArtifactoryPath("https://lts.artifactory.cm.volvocars.biz/artifactory/PT/carport_deliveries/DBC/"+file,
                               auth=(args.user, args.password))
    # Write the content of the DBC file to the workspace of the machine
    if not os.path.exists(args.ws + "\\SWDC_files"):
        os.mkdir(args.ws + "\\SWDC_files")
    with path.open() as read_file:
        with open(args.ws + "\\SWDC_files\\" + file, "wb") as out:
            out.write(read_file.read())

# Run script to get IF-list
get_interfacelist_from_tag.main(args.ws + "\\pt_pcc\\", tag_name, args.ws)
