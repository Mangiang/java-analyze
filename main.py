import argparse
import re
from os import path, walk

from git import Git
from javalang import parse
from javalang.tree import CompilationUnit, MethodDeclaration, FieldDeclaration, ClassDeclaration, InterfaceDeclaration

from src.ClassData import ClassData
from src.FeignData import FeignData
from src.InterfaceData import InterfaceData

ignore = [r'\.git/', r'\.gitignore']
whitelist = [r'.+\.java']
classes = {}
interfaces = {}
feign_clients = {}
rest_controllers = []


def find_classes(treeObj: CompilationUnit):
    for path, node in treeObj.filter(ClassDeclaration):
        classes[node.name] = ClassData(node)


def find_interfaces(treeObj: CompilationUnit):
    for path, node in treeObj.filter(InterfaceDeclaration):
        interfaces[node.name] = InterfaceData(node)


def find_fields(treeObj: CompilationUnit):
    fields = []
    for path, node in treeObj.filter(FieldDeclaration):
        fields.append(node)
    return fields


def find_request_mapping(treeObj: CompilationUnit):
    mappings = []
    for path, node in treeObj.filter(MethodDeclaration):
        for annotation in node.annotations:
            if annotation.name == "RequestMapping":
                mappings.append(node)
    return mappings


def analyze_rest_controllers():
    all_types = {}
    all_types.update(classes)
    all_types.update(interfaces)
    for cont in rest_controllers:
        methods = [meth for meth in cont.methods.values()]
        while len(methods) != 0:
            method = methods.pop()
            tpm_invocations = method.method_invocations
            for invoc in tpm_invocations:
                if invoc.qualifier in cont.fields:
                    new_meth = invoc.member
                    new_type = cont.fields[invoc.qualifier].type
                    if new_type in all_types:
                        if new_meth in all_types[new_type].methods:
                            new_type_data = all_types[new_type]
                            if new_type_data.is_feign_client:
                                feign_data = FeignData(new_type_data.feign_name, new_type_data.methods[new_meth].mapping)
                                if method.name not in cont.feign_calls:
                                    cont.feign_calls[method.mapping] = [feign_data]
                                else:
                                    cont.feign_calls[method.mapping].append(feign_data)
                            else:
                                methods.append(new_type_data.methods[new_meth])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze Java code.')
    parser.add_argument('--directory', '-d', type=str, help='The target directory')
    parser.add_argument('--repository', '-r', type=str, help='The repository https or ssh url')

    args = parser.parse_args()
    gitrepo: str = args.repository.split('/')[-1]
    gitrepo = gitrepo.replace('.git', '')
    repo_dir = path.normpath(path.join(path.dirname(__file__), gitrepo))
    if not path.exists(repo_dir):
        Git(args.directory).clone(args.repository)

    blacklist_regexes = []
    for blacklist in ignore:
        blacklist_regexes.append(re.compile(blacklist))
    whitelist_regexes = []
    for whitelisted in whitelist:
        whitelist_regexes.append(re.compile(whitelisted))

    fnames = []
    for root, d_names, f_names in walk(gitrepo):
        for f in f_names:
            file_path = path.join(root, f)
            if any([regex.match(file_path) for regex in blacklist_regexes]):
                continue
            if any([regex.match(file_path) for regex in whitelist_regexes]):
                fnames.append(file_path)

    # print("fname = %s" % fname)

    for fname in fnames:
        treeObj = None
        with open(fname, 'r') as f:
            treeObj = parse.parse(f.read())
        find_classes(treeObj)
        find_interfaces(treeObj)
    rest_controllers = [cont for cont in classes.values() if cont.is_rest_controller]
    feign_clients = {interface.name: interface for interface in interfaces.values() if interface.is_feign_client}

    analyze_rest_controllers()

    for cont in rest_controllers:
        for name, feign_calls in cont.feign_calls.items():
            for feign_call in feign_calls:
                print(f'[{cont.name}] {name} => {feign_call.name}{feign_call.endpoint}')