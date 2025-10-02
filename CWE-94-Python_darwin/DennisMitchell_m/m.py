import ast, dictionary, fractions, functools, itertools, locale, numpy, operator, parser, sys

import re as regex
from sympy import *

code_page  = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶'''
code_page += '''°¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ƁƇƊƑƓƘⱮƝƤƬƲȤɓƈɗƒɠɦƙɱɲƥʠɼʂƭʋȥẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭụṿẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''

str_digit = '0123456789'
str_lower = 'abcdefghijklmnopqrstuvwxyz'
str_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

inf = float('inf')
nan = float('nan')

class attrdict(dict):
	def __init__(self, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.__dict__ = self

def arities(links):
	return [link.arity for link in links]

def create_chain(chain, arity):
	return attrdict(
		arity = arity,
		call = lambda x = None, y = None: variadic_chain(chain, (x, y))
	)

def create_literal(string):
	return attrdict(
		arity = 0,
		call = lambda: listify(eval(string))
	)

def copy(atom, value):
	atom.call = lambda: value
	return value

def conv_dyadic_integer(link, larg, rarg):
	try:
		iconv_larg = int(larg)
		try:
			iconv_rarg = int(rarg)
			return link(iconv_larg, iconv_rarg)
		except:
			return iconv_larg
	except:
		try:
			return int(rarg)
		except:
			return 0

def conv_monadic_integer(link, arg):
	try:
		return link(int(arg))
	except:
		return 0

def depth(link):
	if type(link) != list:
		return 0
	if not link:
		return 1
	return 1 + max(map(depth, link))

def dyadic_chain(chain, args):
	larg, rarg = args
	for link in chain:
		if link.arity < 0:
			link.arity = 2
	if chain and arities(chain[0:3]) == [2, 2, 2]:
		ret = dyadic_link(chain[0], args)
		chain = chain[1:]
	elif leading_constant(chain):
		ret = niladic_link(chain[0])
		chain = chain[1:]
	else:
		ret = larg
	while chain:
		if arities(chain[0:3]) == [2, 2, 0] and leading_constant(chain[2:]):
			ret = dyadic_link(chain[1], (dyadic_link(chain[0], (ret, rarg)), niladic_link(chain[2])))
			chain = chain[3:]
		elif arities(chain[0:2]) == [2, 2]:
			ret = dyadic_link(chain[0], (ret, dyadic_link(chain[1], args)))
			chain = chain[2:]
		elif arities(chain[0:2]) == [2, 0]:
			ret = dyadic_link(chain[0], (ret, niladic_link(chain[1])))
			chain = chain[2:]
		elif arities(chain[0:2]) == [0, 2]:
			ret = dyadic_link(chain[1], (niladic_link(chain[0]), ret))
			chain = chain[2:]
		elif chain[0].arity == 2:
			ret = dyadic_link(chain[0], (ret, rarg))
			chain = chain[1:]
		elif chain[0].arity == 1:
			ret = monadic_link(chain[0], ret)
			chain = chain[1:]
		else:
			output(ret)
			ret = niladic_link(chain[0])
			chain = chain[1:]
	return ret

def dyadic_link(link, args, conv = True, lflat = False, rflat = False):
	larg, rarg = args
	lflat = lflat or not hasattr(link, 'ldepth')
	rflat = rflat or not hasattr(link, 'rdepth')
	larg_depth = lflat or depth(larg)
	rarg_depth = rflat or depth(rarg)
	if (lflat or link.ldepth == larg_depth) and (rflat or link.rdepth == rarg_depth):
		if conv and hasattr(link, 'conv'):
			return link.conv(link.call, larg, rarg)
		return link.call(larg, rarg)
	conv = conv and hasattr(link, 'conv')
	if not lflat and larg_depth < link.ldepth:
		return dyadic_link(link, ([larg], rarg))
	if not rflat and rarg_depth < link.rdepth:
		return dyadic_link(link, (larg, [rarg]))
	if not rflat and (lflat or larg_depth - rarg_depth < link.ldepth - link.rdepth):
		return [dyadic_link(link, (larg, y)) for y in rarg]
	if not lflat and (rflat or larg_depth - rarg_depth > link.ldepth - link.rdepth):
		return [dyadic_link(link, (x, rarg)) for x in larg]
	return [dyadic_link(link, (x, y)) for x, y in zip(*args)] + larg[len(rarg) :] + rarg[len(larg) :]

def flatten(argument):
	flat = []
	if type(argument) == list:
		for item in argument:
			flat += flatten(item)
	else:
		flat.append(argument)
	return flat

def from_base(digits, base):
	integer = 0
	for digit in digits:
		integer = base * integer + digit
	return integer

def from_exponents(exponents):
	integer = 1
	for index, exponent in enumerate(exponents):
		integer *= ntheory.generate.prime(index + 1) ** exponent
	return integer

def identity(argument):
	return argument

def iterable(argument, make_digits = False, make_range = False):
	the_type = type(argument)
	if the_type == list:
		return argument
	if the_type != str and make_digits:
		return to_base(argument, 10)
	if the_type != str and make_range:
		return range(1, int(argument) + 1)
	return [argument]

def index(haystack, needle):
	for index, item in enumerate(haystack):
		if item == needle:
			return 1 + index
	return 0

def isqrt(number):
	a = number
	b = (a + 1) // 2
	while b < a:
		a = b
		b = (a + number // a) // 2
	return int(a)

def is_string(iterable):
	if type(iterable) != list:
		return False
	return all(map(lambda t: type(t) == str, iterable))

def m_eval(code, arguments):
	return variadic_chain(parse_code(code)[-1] if code else '', arguments)

def m_uneval(argument, top = True):
	the_type = type(argument)
	if the_type in (float, int):
		return m_uneval_real(argument)
	if the_type == complex:
		return m_uneval_real(argument.real) + 'ı' + m_uneval_real(argument.imag)
	if the_type == str:
		return '”' + argument
	if all(map(is_string, argument)):
		strings = [''.join(string) for string in argument]
		if all(map(lambda t: code_page.find(t) < 250, ''.join(strings))):
			return '“' + '“'.join(strings) + '”'
	if is_string(argument):
		string = ''.join(argument)
		if all(map(lambda t: code_page.find(t) < 250, string)):
			return '“' + string + '”'
	middle = ','.join(m_uneval(item, top = False) for item in argument)
	return middle if top else '[' + middle + ']'

def m_uneval_real(number):
	string = str(number if number % 1 else int(number))
	return string.lstrip('0') if number else string

def join(array, glue):
	array = iterable(array)
	last = array.pop() if array else []
	glue = iterable(glue)
	ret = []
	for item in array:
		ret += iterable(item) + glue
	return ret + iterable(last)

def last_input():
	if len(sys.argv) > 3:
		return safe_eval(sys.argv[-1])
	return safe_eval(input())

def leading_constant(chain):
	return chain and arities(chain) + [1] < [0, 2] * len(chain)

def listify(iterable, dirty = False):
	the_type = type(iterable)
	if the_type == str and dirty:
		return list(iterable)
	if not hasattr(iterable,'__iter__') or (the_type == str and len(iterable) == 1):
		return iterable
	return list(listify(item, dirty) for item in iterable)

def loop_until_loop(link, args, return_all = False, return_loop = False):
	ret, rarg = args
	cumret = []
	while True:
		cumret.append(ret)
		larg = ret
		ret = variadic_link(link, (larg, rarg))
		rarg = larg
		if ret in cumret:
			if return_all:
				return cumret
			if return_loop:
				return cumret[index(cumret, ret) - 1 :]
			return larg

def nfind(links, args):
	larg, rarg = args
	matches = variadic_link(links[1], args) if len(links) == 2 else last_input()
	found = []
	while len(found) < matches:
		if variadic_link(links[0], (larg, rarg)):
			found.append(larg)
		larg += 1
	return found

def max_arity(links):
	return max(arities(links)) if min(arities(links)) > -1 else ~max(arities(links))

def monadic_chain(chain, arg):
	for link in chain:
		if link.arity < 0:
			link.arity = max(1, link.arity)
	if leading_constant(chain):
		ret = niladic_link(chain[0])
		chain = chain[1:]
	else:
		ret = arg
	while chain:
		if arities(chain[0:2]) == [2, 1]:
			ret = dyadic_link(chain[0], (ret, monadic_link(chain[1], arg)))
			chain = chain[2:]
		elif arities(chain[0:2]) == [2, 0]:
			ret = dyadic_link(chain[0], (ret, niladic_link(chain[1])))
			chain = chain[2:]
		elif arities(chain[0:2]) == [0, 2]:
			ret = dyadic_link(chain[1], (niladic_link(chain[0]), ret))
			chain = chain[2:]
		elif chain[0].arity == 2:
			ret = dyadic_link(chain[0], (ret, arg))
			chain = chain[1:]
		elif chain[0].arity == 1:
			ret = monadic_link(chain[0], ret)
			chain = chain[1:]
		else:
			output(ret)
			ret = niladic_link(chain[0])
			chain = chain[1:]
	return ret

def monadic_link(link, arg, flat = False, conv = True):
	flat = flat or not hasattr(link, 'ldepth')
	arg_depth = flat or depth(arg)
	if flat or link.ldepth == arg_depth:
		if conv and hasattr(link, 'conv'):
			return link.conv(link.call, arg)
		return link.call(arg)
	conv = conv and hasattr(link, 'conv')
	if link.ldepth > arg_depth:
		return monadic_link(link, [arg], conv = conv)
	return [monadic_link(link, z, conv = conv) for z in arg]

def multiset_difference(left, right):
	result = iterable(left)[::-1]
	for element in iterable(right):
		if element in result:
			result.remove(element)
	return result[::-1]

def multiset_intersect(left, right):
	right = iterable(right)[:]
	result = []
	for element in iterable(left):
		if element in right:
			result.append(element)
			right.remove(element)
	return result

def multiset_symdif(left, right):
	return multiset_union(multiset_difference(left, right), multiset_difference(right, left))

def multiset_union(left, right):
	return left + multiset_difference(right, left)

def niladic_chain(chain):
	if not chain or chain[0].arity > 0:
		return monadic_chain(chain, 0)
	return monadic_chain(chain[1:], chain[0].call())

def niladic_link(link):
	return link.call()

def ntimes(links, args, cumulative = False):
	ret, rarg = args
	repetitions = variadic_link(links[1], args) if len(links) == 2 else last_input()
	if cumulative:
		cumret = [0] * repetitions
	for index in range(repetitions):
		if cumulative:
			cumret[index] = ret
		larg = ret
		ret = variadic_link(links[0], (larg, rarg))
		rarg = larg
	return cumret + [ret] if cumulative else ret

def overload(operators, *args):
	for operator in operators:
		try:
			ret = operator(*args)
		except:
			pass
		else:
			return ret

def parse_code(code):
	lines = regex_flink.findall(code)
	links = [[] for line in lines]
	for index, line in enumerate(lines):
		chains = links[index]
		for word in regex_chain.findall(line):
			chain = []
			arity = str_arities.find(word[0])
			for token in regex_token.findall(word):
				if token in atoms:
					chain.append(atoms[token])
				elif token in quicks:
					popped = []
					while not quicks[token].condition(popped) and (chain or chains):
						popped.insert(0, chain.pop() if chain else chains.pop())
					chain += quicks[token].quicklink(popped, links, index)
				elif token in hypers:
					x = chain.pop() if chain else chains.pop()
					chain.append(hypers[token](x, links))
				else:
					chain.append(create_literal(regex_liter.sub(parse_literal, token)))
			chains.append(create_chain(chain, arity))
	return links

def parse_literal(literal_match):
	literal = literal_match.group(0)
	if literal[0] == '”':
		return repr(literal[1:])
	elif literal[0] == '“':
		if literal[-1] in '«»‘’”':
			mode = literal[-1]
			literal = literal[:-1]
		else:
			mode = ''
		parsed = literal.split('“')[1:]
		if mode == '»':
			parsed = [sss(string).replace('¶', '\n') for string in parsed]
		else:
			parsed = [string.replace('¶', '\n') for string in parsed]
		parsed = [[string] if len(string) == 1 else string for string in parsed]
		if len(parsed) == 1:
			parsed = parsed[0]
		return repr(parsed)
	else:
		parsed = sympify('+ 1j *'.join([
			repr(sympify('* 10 **'.join(['-1' if part == '-' else (part + '5' if part[-1:] == '.' else part) or repr(2 * index + 1)
			for index, part in enumerate(component.split('ȷ'))]), rational = True) if component else index)
			for index, component in enumerate(literal.split('ı'))
		]), rational = True)
		return 'sympify(%s, rational = True)'%repr(str(parsed))

def Pi(number):
	return gamma(number + 1)

def powerset(array):
	array = iterable(array, make_range = True)
	ret = []
	for t in range(len(array) + 1):
		ret += listify(itertools.combinations(array, t))
	return ret

def rld(runs):
	return list(itertools.chain(*[[u] * v for u, v in runs]))

def rotate_left(array, units):
	array = iterable(array)
	length = len(array)
	return array[units % length :] + array[: units % length] if length else []

def safe_eval(string, dirty = True):
	return listify(ast.literal_eval(string), dirty)

def sparse(link, args, indices):
	larg = args[0]
	indices = [index - 1 if index > 0 else index - 1 + len(larg) for index in iterable(variadic_link(indices, args))]
	ret = iterable(variadic_link(link, args))
	return [ret[t % len(ret)] if t in indices else u for t, u in enumerate(larg)]

def split_at(iterable, needle):
	chunk = []
	for element in iterable:
		if element == needle:
			yield chunk
			chunk = []
		else:
			chunk.append(element)
	yield chunk

def sss(compressed):
	decompressed = ''
	integer = from_base([code_page.find(char) + 1 for char in compressed], 250)
	while integer:
		integer, mode = divmod(integer, 3)
		if mode == 0:
			integer, code = divmod(integer, 96)
			decompressed += code_page[code + 32]
		else:
			flag_swap = False
			flag_space = decompressed != ''
			if mode == 2:
				integer, flag = divmod(integer, 3)
				flag_swap = flag != 1
				flag_space ^= flag != 0
			integer, short = divmod(integer, 2)
			the_dictionary = (dictionary.long, dictionary.short)[short]
			integer, index = divmod(integer, len(the_dictionary))
			word = the_dictionary[index]
			if flag_swap:
				word = word[0].swapcase() + word[1:]
			if flag_space:
				word = ' ' + word
			decompressed += word
	return decompressed

def stringify(iterable, recurse = True):
	if type(iterable) != list:
		return iterable
	if str in map(type, iterable) and not list in map(type, iterable) or not iterable:
		return ''.join(map(str, iterable))
	iterable = [stringify(item) for item in iterable]
	return stringify(iterable, False) if recurse else iterable

def symmetric_mod(number, half_divisor):
	modulus = number % (2 * half_divisor)
	return modulus - 2 * half_divisor * (modulus > half_divisor)

def trim(trimmee, trimmer, left = False, right = False):
	lindex = 0
	rindex = len(trimmee)
	if left:
		while lindex < rindex and trimmee[lindex] in trimmer:
			lindex += 1
	if right:
		while lindex < rindex and trimmee[rindex - 1] in trimmer:
			rindex -= 1
	return trimmee[lindex:rindex]

def try_eval(string):
	try:
		return safe_eval(string)
	except:
		return listify(string, True)

def to_base(integer, base, bijective = False):
	if integer == 0:
		return [0] * (not bijective)
	if bijective:
		base = abs(base)
	if base == 0:
		return [integer]
	if base == -1:
		digits = [1, 0] * abs(integer)
		return digits[:-1] if integer > 0 else digits
	sign = -1 if integer < 0 and base > 0 else 1
	integer *= sign
	if base == 1:
		return [sign] * integer
	digits = []
	while integer:
		integer -= bijective
		integer, digit = divmod(integer, base)
		digit += bijective
		if digit < 0:
			integer += 1
			digit -= base
		digits.append(sign * digit)
	return digits[::-1]

def to_case(argument, lower = False, swap = False, title = False, upper = False):
	ret = []
	last_item = ''
	for item in argument:
		if type(item) == str:
			if lower:
				ret.append(item.lower())
			elif swap:
				ret.append(item.swapcase())
			elif title:
				ret.append(item.lower() if type(last_item) == str and last_item in str_upper + str_lower else item.upper())
			elif upper:
				ret.append(item.upper())
		else:
			ret.append(item)
		last_item = item
	return ret

def to_exponents(integer):
	if integer == 1:
		return []
	pairs = ntheory.factor_.factorint(integer)
	exponents = []
	for prime in ntheory.generate.primerange(2, max(pairs) + 1):
		if prime in pairs:
			exponents.append(pairs[prime])
		else:
			exponents.append(0)
	return exponents

def unicode_to_m(string):
	return ''.join(chr(code_page.find(char)) for char in str(string).replace('\n', '¶') if char in code_page)

def unique(iterable):
	result = []
	for element in iterable:
		if not element in result:
			result.append(element)
	return result

def variadic_chain(chain, args):
	args = list(filter(None.__ne__, args))
	if len(args) == 0:
		return niladic_chain(chain)
	if len(args) == 1:
		return monadic_chain(chain, args[0])
	if len(args) == 2:
		return dyadic_chain(chain, args)

def variadic_link(link, args, flat = False, lflat = False, rflat = False):
	if link.arity < 0:
		args = list(filter(None.__ne__, args))
		link.arity = len(args)
	if link.arity == 0:
		return niladic_link(link)
	if link.arity == 1:
		return monadic_link(link, args[0], flat)
	if link.arity == 2:
		return dyadic_link(link, args, lflat, rflat)

def while_loop(link, condition, args, cumulative = False):
	ret, rarg = args
	cumret = []
	while variadic_link(condition, (ret, rarg)):
		if cumulative:
			cumret.append(ret)
		larg = ret
		ret = variadic_link(link, (larg, rarg))
		rarg = larg
	return cumret + [ret] if cumulative else ret

def output(argument, end = '', transform = stringify):
	if locale.getdefaultlocale()[1][0:3] == 'UTF':
		print(transform(argument), end = end)
	else:
		print(unicode_to_m(transform(argument)), end = unicode_to_m(end))
	return argument

atoms = {
	'³': attrdict(
		arity = 0,
		call = lambda: 256
	),
	'⁴': attrdict(
		arity = 0,
		call = lambda: 16
	),
	'⁵': attrdict(
		arity = 0,
		call = lambda: 10
	),
	'⁶': attrdict(
		arity = 0,
		call = lambda: ' '
	),
	'⁷': attrdict(
		arity = 0,
		call = lambda: '\n'
	),
	'A': attrdict(
		arity = 1,
		ldepth = 0,
		call = abs
	),
	'a': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: x and y
	),
	'ȧ': attrdict(
		arity = 2,
		call = lambda x, y: x and y
	),
	'ạ': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: abs(x - y)
	),
	'B': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: to_base(z, 2)
	),
	'Ḅ': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: from_base(z, 2)
	),
	'Ḃ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z % 2
	),
	'b': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: to_base(x, y)
	),
	'ḅ': attrdict(
		arity = 2,
		ldepth = 1,
		rdepth = 0,
		call = lambda x, y: from_base(x, y)
	),
	'ḃ': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: to_base(x, y, bijective = True)
	),
	'C': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: 1 - z
	),
	'Ċ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: overload((ceil, identity), z)
	),
	'c': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: Pi(x) / Pi(x - y) / Pi(y)
	),
	'ċ': attrdict(
		arity = 2,
		call = lambda x, y: iterable(x).count(y)
	),
	'ƈ': attrdict(
		arity = 0,
		call = lambda: sys.stdin.read(1)
	),
	'D': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: to_base(z, 10)
	),
	'Ḍ': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: from_base(z, 10)
	),
	'Ḋ': attrdict(
		arity = 1,
		call = lambda z: iterable(z)[1:]
	),
	'd': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: list(divmod(x, y))
	),
	'ḍ': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: int(y % x == 0 if x else y == 0)
	),
	'Ė': attrdict(
		arity = 1,
		call = lambda z: [[t + 1, u] for t, u in enumerate(iterable(z))]
	),
	'e': attrdict(
		arity = 2,
		call = lambda x, y: int(x in iterable(y))
	),
	'F': attrdict(
		arity = 1,
		call = flatten
	),
	'Ḟ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: overload((floor, identity), z)
	),
	'f': attrdict(
		arity = 2,
		call = lambda x, y: [t for t in iterable(x) if t in iterable(y)]
	),
	'ḟ': attrdict(
		arity = 2,
		call = lambda x, y: [t for t in iterable(x) if not t in iterable(y)]
	),
	'g': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = fractions.gcd
	),
	'Ɠ': attrdict(
		arity = 0,
		call = lambda: safe_eval(input())
	),
	'ɠ': attrdict(
		arity = 0,
		call = lambda: listify(input(), dirty = True)
	),
	'H': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z / 2
	),
	'Ḥ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z * 2
	),
	'Ḣ': attrdict(
		arity = 1,
		call = lambda z: iterable(z).pop(0) if iterable(z) else 0
	),
	'ḣ': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: iterable(x)[:y]
	),
	'I': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: [z[i] - z[i - 1] for i in range(1, len(z))]
	),
	'İ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: S(1) / z
	),
	'i': attrdict(
		arity = 2,
		call = index
	),
	'ị': attrdict(
		arity = 2,
		ldepth = 0,
		call = lambda x, y, I = iterable: I(y)[(int(x) - 1) % len(I(y))] if int(x) == x else [I(y)[(floor(x) - 1) % len(I(y))], I(y)[(ceil(x) - 1) % len(I(y))]]
	),
	'j': attrdict(
		arity = 2,
		call = join
	),
	'L': attrdict(
		arity = 1,
		call = len
	),
	'l': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = log
	),
	'ḷ': attrdict(
		arity = 2,
		call = lambda x, y: x
	),
	'M': attrdict(
		arity = 1,
		call = lambda z: [u + 1 for u, v in enumerate(z) if v == max(z)]
	),
	'Ṃ': attrdict(
		arity = 1,
		call = lambda z: min(iterable(z)) if iterable(z) else 0
	),
	'Ṁ': attrdict(
		arity = 1,
		call = lambda z: max(iterable(z)) if iterable(z) else 0
	),
	'm': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: iterable(x)[::y] if y else iterable(x) + iterable(x)[::-1]
	),
	'N': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: -z
	),
	'Ṅ': attrdict(
		arity = 1,
		call = lambda z: output(z, end = '\n')
	),
	'O': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: ord(z) if type(z) == str else z
	),
	'Ọ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: chr(int(z)) if type(z) != str else z
	),
	'Ȯ': attrdict(
		arity = 1,
		call = output
	),
	'o': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: x or y
	),
	'ȯ': attrdict(
		arity = 2,
		call = lambda x, y: x or y
	),
	'P': attrdict(
		arity = 1,
		call = lambda z: functools.reduce(lambda x, y: dyadic_link(atoms['×'], (x, y)), z, 1) if type(z) == list else z
	),
	'Ṗ': attrdict(
		arity = 1,
		call = lambda z: iterable(z)[:-1]
	),
	'p': attrdict(
		arity = 2,
		call = lambda x, y: listify(itertools.product(iterable(x, make_range = True), iterable(y, make_range = True)))
	),
	'ṗ': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: listify(itertools.product(*([iterable(x, make_range = True)] * y)))
	),
	'Q': attrdict(
		arity = 1,
		call = unique
	),
	'R': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: list(range(1, int(z) + 1) or range(int(z), -int(z) + 1))
	),
	'Ṛ': attrdict(
		arity = 1,
		call = lambda z: iterable(z, make_digits = True)[::-1]
	),
	'Ṙ': attrdict(
		arity = 1,
		call = lambda z: output(z, transform = m_uneval)
	),
	'r': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: list(range(int(x), int(y) + 1) or range(int(x), int(y) - 1, -1))
	),
	'ṙ': attrdict(
		arity = 2,
		rdepth = 0,
		call = rotate_left
	),
	'ṛ': attrdict(
		arity = 2,
		call = lambda x, y: y
	),
	'S': attrdict(
		arity = 1,
		call = lambda z: functools.reduce(lambda x, y: dyadic_link(atoms['+'], (x, y)), z, 0) if type(z) == list else z
	),
	'Ṡ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: (z > 0) - (z < 0)
	),
	'Ṣ': attrdict(
		arity = 1,
		call = lambda z: sorted(iterable(z, make_digits = True))
	),
	's': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: [iterable(x)[i : i + y] for i in range(0, len(iterable(x)), y)]
	),
	'ṡ': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: [iterable(x)[i : i + y] for i in range(len(iterable(x)) - y + 1)]
	),
	'ṣ': attrdict(
		arity = 2,
		call = lambda x, y: listify(split_at(x, y))
	),
	'T': attrdict(
		arity = 1,
		call = lambda z: [u + 1 for u, v in enumerate(z) if v]
	),
	'Ṭ': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: [int(t + 1 in iterable(z)) for t in range(max(iterable(z)))]
	),
	'Ṫ': attrdict(
		arity = 1,
		call = lambda z: iterable(z).pop() if iterable(z) else 0
	),
	't': attrdict(
		arity = 2,
		call = lambda x, y: trim(x, iterable(y), left = True, right = True)
	),
	'ṫ': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: iterable(x)[y - 1 :]
	),
	'U': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: z[::-1]
	),
	'Ụ': attrdict(
		arity = 1,
		call = lambda z: sorted(range(1, len(iterable(z)) + 1), key = lambda t: iterable(z)[t - 1])
	),
	'V': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: m_eval(''.join(map(str, z)), [])
	),
	'Ṿ': attrdict(
		arity = 1,
		call = lambda z: listify(m_uneval(z))
	),
	'v': attrdict(
		arity = 2,
		ldepth = 1,
		call = lambda x, y: m_eval(''.join(map(str, x)), [y])
	),
	'W': attrdict(
		arity = 1,
		call = lambda z: [z]
	),
	'x': attrdict(
		arity = 2,
		ldepth = 1,
		call = lambda x, y: rld(zip(x, y if depth(y) else [y] * len(x)))
	),
	'ẋ': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: iterable(x) * int(y)
	),
	'Z': attrdict(
		arity = 1,
		call = lambda z: listify(map(lambda t: filter(None.__ne__, t), itertools.zip_longest(*map(iterable, z))))
	),
	'z': attrdict(
		arity = 2,
		call = lambda x, y: listify(itertools.zip_longest(*map(iterable, x), fillvalue = y))
	),
	'ż': attrdict(
		arity = 2,
		call = lambda x, y: listify(map(lambda z: filter(None.__ne__, z), itertools.zip_longest(iterable(x), iterable(y))))
	),
	'!': attrdict(
		arity = 1,
		ldepth = 0,
		call = Pi
	),
	'<': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: int(x < y)
	),
	'=': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: int(x == y)
	),
	'>': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: int(x > y)
	),
	':': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.floordiv
	),
	',': attrdict(
		arity = 2,
		call = lambda x, y: [x, y]
	),
	';': attrdict(
		arity = 2,
		call = lambda x, y: iterable(x) + iterable(y)
	),
	'+': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.add
	),
	'_': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.sub
	),
	'×': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.mul
	),
	'÷': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.truediv
	),
	'%': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.mod
	),
	'*': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = operator.pow
	),
	'&': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		conv = conv_dyadic_integer,
		call = operator.and_
	),
	'^': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		conv = conv_dyadic_integer,
		call = operator.xor
	),
	'|': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		conv = conv_dyadic_integer,
		call = operator.or_
	),
	'~': attrdict(
		arity = 1,
		ldepth = 0,
		conv = conv_monadic_integer,
		call = lambda z: ~z
	),
	'²': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z ** 2
	),
	'½': attrdict(
		arity = 1,
		ldepth = 0,
		call = sqrt
	),
	'°': attrdict(
		arity = 1,
		ldepth = 0,
		call = rad
	),
	'¬': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: int(not z)
	),
	'‘': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z + 1
	),
	'’': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: z - 1
	),
	'«': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = min
	),
	'»': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = max
	),
	'⁼': attrdict(
		arity = 2,
		call = lambda x, y: int(x == y)
	),
	'®': attrdict(
		arity = 0,
		call = lambda: 0
	),
	'¹': attrdict(
		arity = 1,
		call = identity
	),
	'ÆA': attrdict(
		arity = 1,
		ldepth = 0,
		call = cos
	),
	'ÆẠ': attrdict(
		arity = 1,
		ldepth = 0,
		call = acos
	),
	'ÆC': attrdict(
		arity = 1,
		ldepth = 0,
		call = ntheory.generate.primepi
	),
	'ÆD': attrdict(
		arity = 1,
		ldepth = 0,
		call = ntheory.factor_.divisors
	),
	'ÆE': attrdict(
		arity = 1,
		ldepth = 0,
		call = to_exponents
	),
	'ÆẸ': attrdict(
		arity = 1,
		ldepth = 1,
		call = from_exponents
	),
	'ÆF': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: [[x, y] for x, y in ntheory.factor_.factorint(z).items()]
	),
	'Æe': attrdict(
		arity = 1,
		ldepth = 0,
		call = exp
	),
	'Æf': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: rld(ntheory.factor_.factorint(z).items())
	),
	'Æl': attrdict(
		arity = 1,
		ldepth = 0,
		call = log
	),
	'ÆN': attrdict(
		arity = 1,
		ldepth = 0,
		call = ntheory.generate.prime
	),
	'Æn': attrdict(
		arity = 1,
		ldepth = 0,
		call = ntheory.generate.nextprime
	),
	'ÆP': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: int(primetest.isprime(z))
	),
	'Æp': attrdict(
		arity = 1,
		ldepth = 0,
		call = ntheory.generate.prevprime
	),
	'ÆR': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: list(ntheory.generate.primerange(2, z + 1))
	),
	'Ær': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: list(numpy.roots(z[::-1]))
	),
	'Æṛ': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: list(numpy.poly(z))[::-1]
	),
	'ÆT': attrdict(
		arity = 1,
		ldepth = 0,
		call = tan
	),
	'ÆṬ': attrdict(
		arity = 1,
		ldepth = 0,
		call = atan
	),
	'ÆṪ': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: ntheory.factor_.totient(z) if z > 0 else 0
	),
	'ÆS': attrdict(
		arity = 1,
		ldepth = 0,
		call = sin
	),
	'ÆṢ': attrdict(
		arity = 1,
		ldepth = 0,
		call = asin
	),
	'Æ²': attrdict(
		arity = 1,
		ldepth = 0,
		call = lambda z: int(isqrt(z) ** 2 == z)
	),
	'Æ½': attrdict(
		arity = 1,
		ldepth = 0,
		call = isqrt
	),
	'Æ°': attrdict(
		arity = 1,
		ldepth = 0,
		call = deg
	),
	'æA': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = atan2
	),
	'Œ!': attrdict(
		arity = 1,
		call = lambda z: listify(itertools.permutations(iterable(z, make_range = True)))
	),
	'ŒḊ': attrdict(
		arity = 1,
		call = depth
	),
	'Œl': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: to_case(z, lower = True)
	),
	'ŒP': attrdict(
		arity = 1,
		call = powerset
	),
	'Œp': attrdict(
		arity = 1,
		call = lambda z: listify(itertools.product(*[iterable(t, make_range = True) for t in z]))
	),
	'ŒṘ': attrdict(
		arity = 1,
		call = lambda z: listify(repr(z))
	),
	'Œs': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: to_case(z, swap = True)
	),
	'Œt': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: to_case(z, title = True)
	),
	'Œu': attrdict(
		arity = 1,
		ldepth = 1,
		call = lambda z: to_case(z, upper = True)
	),
	'æ%': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = symmetric_mod
	),
	'æċ': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: from_base([1] + [0] * len(to_base(x, y)), y)
	),
	'æḟ': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: from_base([1] + [0] * (len(to_base(x, y)) - 1), y)
	),
	'ær': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = round
	),
	'æp': attrdict(
		arity = 2,
		ldepth = 0,
		rdepth = 0,
		call = lambda x, y: float('%%.%dg'%y%x)
	),
	'œc': attrdict(
		arity = 2,
		rdepth = 0,
		call = lambda x, y: listify(itertools.combinations(iterable(x, make_range = True), y))
	),
	'œl': attrdict(
		arity = 2,
		call = lambda x, y: trim(x, iterable(y), left = True)
	),
	'œr': attrdict(
		arity = 2,
		call = lambda x, y: trim(x, iterable(y), right = True)
	),
	'œ&': attrdict(
		arity = 2,
		call = multiset_intersect
	),
	'œ-': attrdict(
		arity = 2,
		call = multiset_difference
	),
	'œ^': attrdict(
		arity = 2,
		call = multiset_symdif
	),
	'œ|': attrdict(
		arity = 2,
		call = multiset_union
	),
	'ØP': attrdict(
		arity = 0,
		call = lambda: pi
	),
	'Øe': attrdict(
		arity = 0,
		call = lambda: E
	),
	'Øg': attrdict(
		arity = 0,
		call = lambda: GoldenRatio
	)
}

quicks = {
	'©': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x = None, y = None: copy(atoms['®'], variadic_link(links[0], (x, y)))
		)]
	),
	'ß': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = -1,
			call = lambda x = None, y = None: variadic_chain(outmost_links[index], (x, y))
		)]
	),
	'¢': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 0,
			call = lambda: niladic_chain(outmost_links[index - 1])
		)]
	),
	'Ç': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 1,
			call = lambda z: monadic_chain(outmost_links[index - 1], z)
		)]
	),
	'ç': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 2,
			call = lambda x, y: dyadic_chain(outmost_links[index - 1], (x, y))
		)]
	),
	'Ñ': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 1,
			call = lambda z: monadic_chain(outmost_links[(index + 1) % len(outmost_links)], z)
		)]
	),
	'ñ': attrdict(
		condition = lambda links: True,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 2,
			call = lambda x, y: dyadic_chain(outmost_links[(index + 1) % len(outmost_links)], (x, y))
		)]
	),
	'¦': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = max_arity(links + [atoms['¹']]),
			call = lambda x, y = None: sparse(links[0], (x, y), links[1])
		)]
	),
	'¡': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: ([links.pop(0)] if len(links) == 2 and links[0].arity == 0 else []) + [attrdict(
			arity = max_arity(links),
			call = lambda x = None, y = None: ntimes(links, (x, y))
		)]
	),
	'¿': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = max(link.arity for link in links),
			call = lambda x = None, y = None: while_loop(links[0], links[1], (x, y))
		)]
	),
	'¤': attrdict(
		condition = lambda links: len(links) > 1 and links[0].arity == 0,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 0,
			call = lambda: niladic_chain(links)
		)]
	),
	'$': attrdict(
		condition = lambda links: len(links) > 1 and not leading_constant(links),
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 1,
			call = lambda z: monadic_chain(links, z)
		)]
	),
	'¥': attrdict(
		condition = lambda links: len(links) > 1 and not leading_constant(links),
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = 2,
			call = lambda x, y: dyadic_chain(links, (x, y))
		)]
	),
	'#': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: ([links.pop(0)] if len(links) == 2 and links[0].arity == 0 else []) + [attrdict(
			arity = max_arity(links),
			call = lambda x = None, y = None: nfind(links, (x, y))
		)]
	),
	'?': attrdict(
		condition = lambda links: len(links) == 3,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = max(link.arity for link in links),
			call = lambda x = None, y = None: variadic_link(links[0], (x, y)) if variadic_link(links[2], (x, y)) else variadic_link(links[1], (x, y))
		)]
	),
	'Ð¡': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: ([links.pop(0)] if len(links) == 2 and links[0].arity == 0 else []) + [attrdict(
			arity = max(link.arity for link in links),
			call = lambda x = None, y = None: ntimes(links, (x, y), cumulative = True)
		)]
	),
	'Ð¿': attrdict(
		condition = lambda links: len(links) == 2,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = max(link.arity for link in links),
			call = lambda x = None, y = None: while_loop(links[0], links[1], (x, y), cumulative = True)
		)]
	),
	'Ðf': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x, y = None: list(filter(lambda t: variadic_link(links[0], (t, y)), x))
		)]
	),
	'Ðḟ': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x, y = None: list(itertools.filterfalse(lambda t: variadic_link(links[0], (t, y)), x))
		)]
	),
	'ÐL': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x = None, y = None: loop_until_loop(links[0], (x, y))
		)]
	),
	'ÐĿ': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x = None, y = None: loop_until_loop(links[0], (x, y), return_all = True)
		)]
	),
	'ÐḶ': attrdict(
		condition = lambda links: links,
		quicklink = lambda links, outmost_links, index: [attrdict(
			arity = links[0].arity,
			call = lambda x = None, y = None: loop_until_loop(links[0], (x, y), return_loop = True)
		)]
	)
}

hypers = {
	'"': lambda link, none = None: attrdict(
		arity = 2,
		call = lambda x, y: [dyadic_link(link, (u, v)) for u, v in zip(iterable(x), iterable(y))] + iterable(x)[len(iterable(y)) :] + iterable(y)[len(iterable(x)) :]
	),
	"'": lambda link, none = None: attrdict(
		arity = link.arity,
		call = lambda x = None, y = None: variadic_link(link, (x, y), flat = True, lflat = True, rflat = True)
	),
	'@': lambda link, none = None: attrdict(
		arity = 2,
		call = lambda x, y: dyadic_link(link, (y, x))
	),
	'/': lambda link, none = None: attrdict(
		arity = 1,
		call = lambda z: functools.reduce(lambda x, y: dyadic_link(link, (x, y)), iterable(z))
	),
	'\\': lambda link, none = None: attrdict(
		arity = 1,
		call = lambda z: list(itertools.accumulate(iterable(z), lambda x, y: dyadic_link(link, (x, y))))
	),
	'{': lambda link, none = None: attrdict(
		arity = 2,
		call = lambda x, y: monadic_link(link, x)
	),
	'}': lambda link, none = None: attrdict(
		arity = 2,
		call = lambda x, y: monadic_link(link, y)
	),
	'€': lambda link, none = None: attrdict(
		arity = link.arity,
		call = lambda x, y = None: [variadic_link(link, (t, y)) for t in iterable(x)]
	),
	'£': lambda index, links: attrdict(
		arity = index.arity,
		call = lambda x = None, y = None: niladic_chain(links[(variadic_link(index, (x, y)) - 1) % (len(links) - 1)])
	),
	'Ŀ': lambda index, links: attrdict(
		arity = max(1, index.arity),
		call = lambda x, y = None: monadic_chain(links[(variadic_link(index, (x, y)) - 1) % (len(links) - 1)], x)
	),
	'ŀ': lambda index, links: attrdict(
		arity = 2,
		call = lambda x, y: dyadic_chain(links[(variadic_link(index, (x, y)) - 1) % (len(links) - 1)], (x, y))
	)
}

str_arities = 'øµð'
str_strings = '“[^«»‘’”]*[«»‘’”]?'
str_charlit = '”.'
str_realdec = '(?:0|-?\d*\.\d*|-?\d+|-)'
str_realnum = str_realdec.join(['(?:', '?ȷ', '?|', ')'])
str_complex = str_realnum.join(['(?:', '?ı', '?|', ')'])
str_literal = '(?:' + str_strings + '|' + str_charlit + '|' + str_complex + ')'
str_litlist = '\[*' + str_literal + '(?:(?:\]*,\[*)' + str_literal + ')*' + '\]*'
str_nonlits = '|'.join(map(regex.escape, list(atoms) + list(quicks) + list(hypers)))

regex_chain = regex.compile('(?:^|[' + str_arities + '])(?:' + str_nonlits + '|' + str_litlist + '| )+')
regex_liter = regex.compile(str_literal)
regex_token = regex.compile(str_nonlits + '|' + str_litlist)
regex_flink = regex.compile('(?=.)(?:[' + str_arities + ']|' + str_nonlits + '|' + str_litlist + '| )*¶?')