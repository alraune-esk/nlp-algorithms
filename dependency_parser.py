class Parser:
    def __init__(self, rules):
        self.rules = rules
        self.stack = ['ROOT']
        self.dependencies = []

    def is_in_dependencies(self, c):
        """
        :param c: an input symbol
        :return: True iff there already exists a dependency to c in the set of dependencies.
        """
        for vi, vj in self.dependencies:
            if vj == c:
                return True
        return False

    def left_arc(self):
        if len(self.stack) == 0 or len(self.input_string) == 0:
            # We ae unable to apply left_arc in this situation, give up.
            return False
        input_char = self.input_string[0] # get first input token.
        input_char_type = input_char.split('_')[0] # each input token is made of a letter and an identifier for its position in the sequence, so that duplicate tokens can be distinguished.
        if [input_char_type, self.stack[-1].split('_')[0]] in self.rules and not self.is_in_dependencies(self.stack[-1]): # stack[-1] is the top of the stack.
            # Since there does not already exist a dependency to the top of the stack, perform a left-arc transition.
            self.dependencies.append([input_char, self.stack[-1]])
            self.stack = self.stack[:-1]
            return True
        return False

    def right_arc(self):
        if len(self.stack) == 0 or len(self.input_string) == 0:
            # We are unable to apply right_arc in this situation, give up.
            return False
        input_char = self.input_string[0]  # get first input token.
        input_char_type = input_char.split('_')[0]
        # check if (top of stack -> input token) is a rule
        # and that the input token does not already exist in the dependencies
        if [self.stack[-1].split('_')[0], input_char_type] in self.rules and not self.is_in_dependencies(input_char):
            # if it is a rule and the input token does not already have a dependency, perform a right-arc transition
            self.dependencies.append([self.stack[-1], input_char])
            self.stack.append(input_char)
            return True
        return False

    def reduce(self):
        if len(self.stack) == 0:
            # We cant reduce an empty stack
            return False
        # we can only perform a reduce if the top of the stack has a dependency
        if self.is_in_dependencies(self.stack[-1]):
            # remove the top of the stack
            self.stack = self.stack[:-1]
            return True
        return False

    def shift(self):
        if len(self.input_string) == 0:
            return False
        self.stack.append(self.input_string[0])
        self.input_string = self.input_string[1:]
        return True

    def print_trace(self):
        print(str(self.stack) + ', ' + str(self.input_string) + ', ' + str(self.dependencies))

    def parse(self, input_string):
        self.input_string = [s + '_' + str(i) for i, s in enumerate(input_string)]  # Append index to each character so that duplicate characters can be distinguished.
        self.stack = ['ROOT']
        self.dependencies = []
        while True:
            is_stuck = True
            for op in [self.left_arc, self.right_arc, self.reduce, self.shift]:
                if op():
                    print(f'Apply {op.__name__}')
                    self.print_trace()
                    is_stuck = False
                    break
            if is_stuck:
                if len(self.stack) > 1:
                    print('PARSING FAILED')
                return self.dependencies


parser = Parser([['ROOT', 'A'],
                 ['A', 'B'],
                 ['B', 'C'],
                 ['C', 'B']
                ])

test_sentences = ['ABC', # Should succeed.
                  'ABCBC', # Should succeed.
                  'BAC'] # Should fail.

for s in test_sentences:
    print(f'parsing {s}:')
    parser.parse(s)
    print()
