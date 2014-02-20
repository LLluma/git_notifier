#!/usr/bin/env python
import os
import sys
import git


def check_status(root_dir):
    directories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
    result = {}

    for module_dir in directories:
        try:
            repo = git.Repo(os.path.join(root_dir, module_dir))
            repoCmd = git.cmd.Git(working_dir=repo.working_dir)
            unpushed = repoCmd.execute(['git', 'log', '--branches',
                                        '--not', '--remotes', '--simplify-by-decoration',
                                        '--decorate', '--oneline'])
            dirty = repoCmd.execute(['git', 'status', '--porcelain', ])
            if unpushed or dirty:
                result[module_dir] = {}
                if unpushed:
                    result[module_dir]['unpushed'] = unpushed
                if dirty:
                    result[module_dir]['dirty'] = dirty
        except git.exc.InvalidGitRepositoryError:
            result[module_dir] = {}
            result[module_dir]['error'] = "Is not git repository"
    os.chdir(root_dir)
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        root_dirs = [os.getcwd(), ]
    else:
        root_dirs = sys.argv[1:]
    for root_dir in root_dirs:
        print "%s\n%s\n" % (root_dir, "=" * len(root_dir))
        result = check_status(root_dir)
        for module, message in result.items():
            print module
            for k, v in message.items():
                print "\t%s\t%s" % (k, v)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: