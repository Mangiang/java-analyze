from javalang.tree import MethodDeclaration, MethodInvocation, ElementValuePair, Literal

from src.MethodInvocationData import MethodInvocationData


class MethodData:
    def __init__(self, data: MethodDeclaration):
        self.data = data
        self.name = data.name
        self.annotations = {ann.name: ann for ann in self.data.annotations}
        self.method_invocations = []
        self.mapping = None
        for ann in self.annotations.values():
            if ann.name == 'RequestMapping':
                for elt in ann.element:
                    if type(elt) == Literal:
                        self.mapping = elt.value.replace('"', '').replace("'", '')
                    if type(elt) == ElementValuePair and (elt.name == 'name' or elt.name == 'value'):
                        self.mapping = elt.value.value.replace('"', '').replace("'", '')
                self.mapping = '/' if self.mapping is None else self.mapping

        for path, node in self.data.filter(MethodInvocation):
            self. method_invocations.append(MethodInvocationData(node, node.qualifier, node.member))