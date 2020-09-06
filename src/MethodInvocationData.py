from javalang.tree import MethodInvocation


class MethodInvocationData:
    def __init__(self, data: MethodInvocation, qualifier, member):
        self.data = data
        self.qualifier = qualifier
        self.member = member