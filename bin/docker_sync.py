#!/usr/bin/env python

from __future__ import print_function
from docker_utils import (get_repos, get_teams, get_permissions, get_members, logout, create_repo, create_team, 
                          add_permissions, add_member, delete_repo, delete_team, delete_permissions, delete_member)
from argparse import ArgumentParser
import yaml
import sys
from os.path import join, dirname, abspath

parser = ArgumentParser(description='Synchronize Docker HUB with yaml configuration file')
parser.add_argument('-u', '--username', dest='username', help="Provide Docker Hub username for synchronization", type=str, default='cmssw')
parser.add_argument('-n', '--disable', dest='dryrun', help="Dry Run mode enabled by default. Disable it to make changes to docker hub", action="store_false", default=True)
args = parser.parse_args()
if not args.dryrun:
  print('==== DRY RUN MODE DISABLED ====')

def update_dockerhub(config_file, docker_hub, username = args.username, team_name = None, repo = None, 
                     team_id = None, yaml_permissions = None, what_to_sync = None, dryrun=args.dryrun):
  dryrun_message = 'Dry run mode enabled, no changes to Docker Hub applied'
  diff_list = [item for item in config_file + docker_hub if item not in config_file or item not in docker_hub]
  for list_item in diff_list:
    if list_item in config_file and list_item not in docker_hub:
      if what_to_sync == 'repos':
        print('Adding repository: "%s"' % list_item)
        print(dryrun_message) if dryrun else print(create_repo(username, list_item)[0])
      elif what_to_sync == 'teams':
        print('Creating team: "%s"' % list_item)
        print(dryrun_message) if dryrun else print(create_team(username, list_item)[0])
      elif what_to_sync == 'permissions':
        print('Adding "%s" permission to "%s" repository for "%s" team:' % (yaml_permissions[list_item], list_item, team_name))
        print(dryrun_message) if dryrun else print(add_permissions(username, list_item, team_id, yaml_permissions[list_item])[0])
      elif what_to_sync == 'members':
        print('Adding member "%s" to "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(add_member(username, team_name, list_item)[0])
    if list_item in docker_hub and list_item not in config_file:
      if what_to_sync == 'repos':
        print('Deleting repository: "%s"' % list_item)
        print(dryrun_message) if dryrun else print('%s repository does not exist in yaml configuration file' % list_item) & sys.exit(1)
      elif what_to_sync == 'teams':
        print('Deleting team: "%s"' % list_item)
        print(dryrun_message) if dryrun else print(delete_team(username, list_item)[0])
      elif what_to_sync == 'permissions':
        print('Deleting permission for "%s" repository from "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(delete_permissions(username, list_item, team_id)[0])
      elif what_to_sync == 'members':
        print('Deleting member "%s" from "%s" team:' % (list_item, team_name))
        print(dryrun_message) if dryrun else print(delete_member(username, team_name, list_item)[0])

yaml_location = join(dirname(dirname(abspath(__file__))), "docker_config.yaml")
with open(yaml_location) as file:
  yaml_file = yaml.load(file, Loader=yaml.FullLoader)
repos_config_dict = yaml_file['repositories']
yaml_repos = []
for signle_repo_config in repos_config_dict:
  yaml_repos += (signle_repo_config.keys())
yaml_teams = yaml_file['teams'].keys()
# UPDATE REPOSITORIES:
print('\n----- Synchronizing repositories for "%s":' % args.username)
hub_repos = get_repos(args.username)
if not hub_repos[0]: print(hub_repos[1]) & sys.exit(1)
if hub_repos[1] == []:
  print('No repositories found. Check Docker Hub username')
  sys.exit(1)
update_dockerhub(yaml_repos, hub_repos[1], what_to_sync='repos')
# UPDATE TEAMS:
print('\n----- Synchronizing teams for "%s":' % args.username)
hub_teams = get_teams(args.username)
if not hub_teams[0]: print(hub_teams[1]) & sys.exit(1)
update_dockerhub(yaml_teams, list(hub_teams[1].keys()), what_to_sync='teams') 
team_acces_map = {}
for team_name in hub_teams[1]:
  team_id = hub_teams[1][team_name]
  yaml_permissions = {}
  if team_name != 'owners':
  # UPDATE PERMISSIONS:
    print('\n----- Synchronizing permissions for "%s" team:' % team_name)
    hub_permissions = get_permissions(args.username, team_name)
    if not hub_permissions[0]: print(hub_permissions[1]) & sys.exit(1)
    for signle_repo_config in repos_config_dict:
      team_acces_map = signle_repo_config.values()[0]
      try:
        yaml_permissions[signle_repo_config.keys()[0]] = team_acces_map[team_name]
      except Exception:
        continue
    if not yaml_permissions:
      print('No repository permissions found in yaml config file for "%s"' % team_name)
      yaml_access_list = []
    else:
      yaml_access_list = yaml_permissions.keys()
    permissions_to_add = {}
    for item in hub_permissions[1].items():
      repository, permission = item[0], item[1]
      if yaml_permissions and yaml_permissions[repository] != permission:
        continue
      permissions_to_add[repository] = permission
    docker_access_list = []
    docker_access_list = permissions_to_add.keys()
    update_dockerhub(yaml_access_list, docker_access_list, team_name=team_name, 
    team_id=team_id, yaml_permissions=yaml_permissions, what_to_sync = 'permissions')
    # UPDATE MEMBERS:
    print('\n----- Synchronizing members for "%s":' % team_name)
    hub_team_members = get_members(args.username, team_name)
    if not hub_team_members[0]: print(hub_team_members[1]) & sys.exit(1)
    members_in_yaml = yaml_file['teams'][team_name]
    if members_in_yaml is None: 
      print('No members found in yaml config file for "%s"' % team_name)
      members_in_yaml = []
    update_dockerhub(members_in_yaml, hub_team_members[1], team_name=team_name, what_to_sync='members')
logout()