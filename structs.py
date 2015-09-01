# coding=utf-8
import struct
import copy

"""
规则：
    Char数组 从内存低地址向高地址排列

"""

class ArrayOperator:

    def __init__(self, lst):
        self.lst = lst

    def __or__(self, rlst):
        """
        最大长度同self.lst
        """
        for i in range(len(self.lst)):
            try:
                self.lst[i] = rlst[i]
            except Exception as e:
                return self.lst
        return self.lst

class Field:

    def __init__(self, number=1, word_length=1):
        assert number >= 1

        self.number = number
        self.word_length = word_length
        self.value = ['\x00' * word_length] * number
        self._is_array = True if number > 1 else False
        self._mask = int('0x' + 'ff' * number * word_length, base=16)

    def _length(self):
        return self.number

    def normalize(self, value):
        raise NotImplementedError()

    def set_value(self, value):
        _normalized_value = self.normalize(value)
        if _normalized_value:
            self.clear()
            self.value = ArrayOperator(self.value) | _normalized_value

    def __str__(self):
        return str(self.value)

    def __deepcopy__(self, *args):
        return type(self)(self.number)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, name):
        if self.number < 2:
            raise TypeError('%s is not an array' % self)

    def clear(self):
        self.value = ['\x00' * self.word_length] * self.number



# class StructMeta(type):

#     def __new__(cls, name, bases, attrs):
#         for k, v in attrs.items():
#             if isinstance(v, Field):
#                 attrs[k] = copy.deepcopy(v)

#         return super().__new__(cls, name, bases, attrs)


class Struct():

    def __init__(self):
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, Field):
                self.__dict__[k] = copy.deepcopy(v)

    def unpack(self):
        pass

    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise Exception('%s does not have field %s' %
                            (self.__class__.__name__, name))

        getattr(self, name).set_value(value)
        return getattr(self, name)

    def __len__(self):
        length = 0
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, Field):
                length += len(v)
        return length


class CharField(Field):

    def normalize(self, value):
        """
            .. note:
                如果不是数组类型，传入值是 int 或者是 str
                如果是数组类型，传入值是list(int), 或者 str, 或者 list(str)
        """
        def normalizer(value):
            if isinstance(value, int):
                value = value & self._mask
                return bytes(bytearray(value.to_bytes((value.bit_length() + 7) // 8, 'big')))

            elif isinstance(value, bytes) or isinstance(value, str):
                return value

        if self._is_array:
            if isinstance(value, list):
                if len(value) < self.number:
                    value = value + [0] * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]


            elif isinstance(value, int):
                return [normalizer(value)]  # 小端表示

            elif isinstance(value, str) or isinstance(value, bytes) or isinstance(value, bytearray):
                if len(value) < self.number:
                    value = value + '\x00' * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]

        else:
            assert isinstance(value, int) or isinstance(value, bytes)

            return [normalizer(value)]

        # if isinstance(value, int):
        #     value = value & self._mask
        #     return bytes(bytearray(value.to_bytes((value.bit_length() + 7) // 8, 'big')).rjust(self.number))
        # elif isinstance(value, str):
        #     return value[:self.number].encode('latin').rjust(self.number)
        # else:
        #     raise TypeError('%s must be int or str' % value)


class Int8Field(Field):

    def normalize(self, value):
        """
            .. note:
                如果不是数组类型，传入值是 int 或者是 str
                如果是数组类型，传入值是list(int), 或者 str, 或者 list(str)
        """
        def normalizer(value):
            if isinstance(value, int):
                value = value & self._mask
                return bytes(bytearray(value.to_bytes((value.bit_length() + 7) // 8, 'big')))

            elif isinstance(value, bytes) or isinstance(value, str):
                return value

        if self._is_array:
            if isinstance(value, str) or isinstance(value, bytes) or isinstance(value, bytearray):
                if len(value) < self.number:
                    value = value + '\x00' * (self.number - len(value))

                return [normalizer(value[i]) for i in range(self.number)]

            elif isinstance(value, list):
                if len(value) < self.number:
                    value = value + [0] * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]
            else:
                value = list(value)
                if len(value) < self.number:
                    value = value + [0] * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]

            # if isinstance(value, list):
            #     if len(value) < self.number:
            #         value = value + [0] * (self.number - len(value))
            #     for i in range(self.number):
            #         self.value[i] = normalizer(value[i])

            # elif isinstance(value, int):
            #     self.value[0] = normalizer(value)  # 小端表示

            # elif isinstance(value, str) or isinstance(value, bytes) or isinstance(value, bytearray):
            #     if len(value) < self.number:
            #         value = value + '\x00' * (self.number - len(value))
            #     for i in range(self.number):
            #         self.value[i] = normalizer(value[i])

            # return self.value
        else:
            assert isinstance(value, int) or isinstance(value, bytes)

            return [normalizer(value)]


class Int16Field(Field):
    def __init__(self, number=1):
        super().__init__(number=number, word_length=2)

    def normalize(self, value):
        """
            .. note:
                如果不是数组类型，传入值是 int 或者是 str
                如果是数组类型，传入值是list(int), 或者 str, 或者 list(str)
        """
        def normalizer(value):
            assert isinstance(value, int) # assert value must be Integer

            if isinstance(value, int):
                value = value & self._mask
                return bytes(bytearray(value.to_bytes((value.bit_length() + 7) // 8, 'big')))

        if self._is_array:
            if isinstance(value, list):
                if len(value) < self.number:
                    value = value + [0] * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]

            elif isinstance(value, int):
                return [normalizer(value)]  # 小端表示

            elif isinstance(value, str) or isinstance(value, bytes) or isinstance(value, bytearray):
                if len(value) < self.number:
                    value = value + '\x00' * (self.number - len(value))
                return [normalizer(value[i]) for i in range(self.number)]

        else:
            assert isinstance(value, int) or isinstance(value, bytes)

            return [normalizer(value)]


class Int32Field(Field):
    pass


class Int64Field(Field):
    pass


class LoginPacket(Struct):
    id = CharField()
    username = CharField(3)
    password = CharField(32)
    test_int16_field = Int16Field()
    test_int16_array_field = Int16Field(4)

a = LoginPacket()

a.id = 5
print(a.id)
a.username = 'aaaa'
print('USERNAME1', a.username)
a.username = 72
print(a.username)
a.test_int16_field = 65534
print(a.test_int16_field)
a.test_int16_array_field = [0x342e, 0x1234, 0xeeee]
print('INT16_ARRAY_FIELD', a.test_int16_array_field)



#print(id(a.username), id(b.username))
#print('Final', a.username, b.username, len(b.username), len(a))

