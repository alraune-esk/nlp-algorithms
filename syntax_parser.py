import json


class TreeNode:
    """
    Class for representing parse trees. Contains some useful utilities for printing and reading/writing to string.
    """
    def from_list(lst):
        root = TreeNode(lst[0])
        root.children = [TreeNode.from_list(ls) for ls in lst[1:]]
        return root

    def from_string(string):
        return TreeNode.from_list(json.loads(string))

    def __init__(self, val):
        self.val = val
        self.children = []

    def to_list(self):
        return [self.val] + [c.to_list() for c in self.children]

    def to_string(self):
        return json.dumps(self.to_list())

    def display(self):
        string = self.val + '\n'
        stack = self.children
        done = False
        while not done:
            done = True
            new_stack = []
            for c in stack:
                string += c.val + '\t'
                if len(c.children) == 0:
                    new_stack.append(TreeNode('\t'))
                else:
                    done = False
                    new_stack.extend(c.children)
            string += '\n'
            stack = new_stack
        return string


with open('train_x.txt', 'r') as f:
    x = [l.split() for l in f.readlines()]
    # Each element of x is a list of words (a sentence).

with open('train_y.txt', 'r') as f:
    y = [TreeNode.from_string(l) for l in f.readlines()]
    # Each element of y is a TreeNode object representing the syntax of the corresponding element of x


# Dictionaries to hold the total number of each grammar rule (e.g. A -> B)
# and the total number of each non terminal (e.g. A, B, C)
rule_count = {}
non_terminal_count = {}


def expand(tree):
    """ Extract the total numbers of each grammar rule and non terminals and update the dictionaries accordingly
        recurse to go through the entire tree

        Args:
            tree (List):  A list representation of the TreeNode
    """
    root = tree[0]
    # in the case that we have 2 child nodes
    # extract the rule (e.g. A -> BC) and update the counts in the dictionaries
    # recurse for the two children nodes
    if len(tree) == 3:
        child1 = tree[1]
        child2 = tree[2]
        rule1 = "" + root + " -> " + child1[0] + "" + child2[0]
        if rule1 in rule_count:
            rule_count[rule1] += 1
        else:
            rule_count[rule1] = 1
        if root in non_terminal_count:
            non_terminal_count[root] += 1
        else:
            non_terminal_count[root] = 1

        expand(child1)
        expand(child2)
    # the case for 1 child node
    # e.g. (B -> w_123)
    # update dictionaries accordingly
    elif len(tree) == 2:
        child = tree[1][0]
        rule = "" + root + " -> " + child
        if rule in rule_count:
            rule_count[rule] += 1
        else:
            rule_count[rule] = 1
        if root in non_terminal_count:
            non_terminal_count[root] += 1
        else:
            non_terminal_count[root] = 1
        expand(child)


def estimate_pcfg(parse_tree):
    """ Estimate the PCFG that generated the training dataset

        Args:
            parse_tree (TreeNode): a TreeNode parse_tree that represents a parse tree
        Output:
            transition_probabilities (List): A list of transitions and their probabilities in the given training set
    """
    for tree in parse_tree:
        expand(tree.to_list())
    transition_probabilities = []
    for transition in rule_count:
        non_terminal = transition.split(' -> ')[0]
        prob = (transition, rule_count[transition] / non_terminal_count[non_terminal])
        transition_probabilities.append(prob)
    return transition_probabilities


print(estimate_pcfg(y))
