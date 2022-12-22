import json
import os

class CodeCommit:
    def __init__(self, profile, account_id, region):
        self.profile = profile
        self.account_id = account_id
        self.region = region
        self.command = f'aws --profile {self.profile} --region {self.region} codecommit'

    def get_merge_conflicts(self, repository, origin_branch, target_branch, merge_type):
        command = f'{self.command} get-merge-conflicts --repository-name {repository} --source-commit-specifier {origin_branch} --destination-commit-specifier {target_branch} --merge-option {merge_type}'
        return json.loads(os.popen(command).read())

    def create_pull_request(self, title, repository, sourceReference, destinationReference):
        command = f'{self.command} create-pull-request --title "{title}" --targets repositoryName={repository},sourceReference={sourceReference},destinationReference={destinationReference}'
        return json.loads(os.popen(command).read())

    def get_repository_arn(self, repository):
        return f'arn:aws:codecommit:{self.region}:{self.account_id}:{repository}'

    def list_tags_for_resource(self, arn):
        command = f'{self.command} list-tags-for-resource --resource-arn {arn}'
        return json.loads(os.popen(command).read())

    def get_repository_tenant_by_its_tags(self, repository):
        arn = self.get_repository_arn(repository)
        repository_tags = self.list_tags_for_resource(arn)
        return repository_tags['tags']['tenant']
    
    def close_pull_request(self, pr_id):
        command = f'{self.command} update-pull-request-status --pull-request-id {pr_id} --pull-request-status CLOSED'
        return json.loads(os.popen(command).read())