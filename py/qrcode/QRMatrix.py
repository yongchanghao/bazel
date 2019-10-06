# from PIL import Image


class QRMatrix:
    """
    The QRMatrix Class that will allow users to encode and decode QR Codes.
    """
    type_of_encoding = {0: "End", 1: "Numeric", 2: "Alphanumeric", 3: "Structred Append", 4: "Byte", 5: "FNC1 in First",
                        7: "Extended Channel Interpretation", 8: "Kanji", 9: "FNC1 in Second"}
    pad_bytes = {0: 236, 1: 17}
    error_correction_levels = {3: "L", 1: "M", 2: "Q", 0: "H"}

    def __init__(self, decode_or_encode, image, ):
        """
        Creates a QRMatrix object. If decode_or_encode is set to decode, then the image_or_text parameter will search
        for a file in the system. It'll then break down the QR code and store data on it. Otherwise, if it's set to
        encode the string into a QR code. Both will still require a call to decode and/or encode.

        When decoding, it begins by using numpy to convert the image_or_text into a binary ndary array. 0 will refer
        to black pixels and 255 will refer to white pixels. Afterwards, it is converted into a list of lists where
        white space is then trimmed and the matrix is then scaled. The version of the matrix is based of the size of
        the matrix provided. Every 4 pixels greater than 21 equates to a larger version.

        :param decode_or_encode:
        :return:
        """
        if decode_or_encode == "decode":
            self.matrix = image.tolist()
            self.__intify_matrix()
            self.__scale_matrix()
            self.version = ((len(self.matrix) - 21) // 4) + 1
        elif decode_or_encode == "encode":
            print("Matrix Maker has not been implemented yet")

    def __str__(self):
        """
        Creates an n x n matrix representation of the QRMatrix object. For this representation, 255 will become 1 to
        balance out the view.

        :return: The String representation of a QRMatrix.
        """
        for row in self.matrix:
            print([i if i != 255 else 1 for i in row])
        return ""

    def __out_of_bounds(self, x, y):
        """
        This function will determine if the matrix is out of bounds. If used on a micro qr code, this function will need
        to be modified. The first and second clauses check if the matrix has stepped out of bounds. The latter two
        clauses checks if the x and y position is on any of the three orientation markers.
        :param x: The x coordinate.
        :param y: The y coordinate.
        :return: A boolean of whether or not the current position is out of bounds.
        """
        if x > len(self.matrix) - 1 or y > len(self.matrix) - 1:
            return True
        elif x < 0 or y < 0:
            return True
        elif x < 9 and (y < 9 or y >= len(self.matrix) - 8):
            return True
        elif x < 9 and y >= len(self.matrix) - 8:
            return True
        else:
            return False

    def __get_error_correction_level(self, traversal):
        """
        Extracts the error correction level from the matrix.
        :return: The error correction level L, M, Q, or H.
        """

        return self.error_correction_levels[self.matrix[8][0] * 1 + self.matrix[8][1] * 2]

    def decode(self):
        """
        Decodes the matrix. First, this preforms a zigzag traversal over the entirety of the matrix. The first 4 bits
        are used to determine what type of representation is used(Alpha-numeric, binary, kanji, etc.). The next 8 bits
        correspond with the length of the word. Every 8 bits after that is a part of the word and is added into it.
        :return: A decoded string of the QR code.
        """
        zig_zag_traversal = self.__traverse_matrix()
        word = ""
        encoding_mode = ""
        decode_function = chr
        try:
            encoding_mode = self.type_of_encoding[self.__decode_bits(zig_zag_traversal, 0, 4)]
        except KeyError:
            print("Non-existing encode mode.")

        length = self.__decode_bits(zig_zag_traversal, 4)
        if encoding_mode == "Byte" or encoding_mode == "Japanese":
            bytes = 8
            decode_function = chr
        elif encoding_mode == "Alphanumeric":
            bytes = 9
            # decode_function =
        elif encoding_mode == "Numeric":
            bytes = 10
            # decode_function =
        else:
            raise Exception(encoding_mode + " has not yet been implemented")
        for i in range((int)(length)):
            word += decode_function((int)(self.__decode_bits(zig_zag_traversal, 12 + i * bytes)))
        return word

    def __within_orientation_markers(self, x, y):
        """
        QR codes greater than version 1 contain certain fixed areas that no data is stored. This helper function
        prevents the traversal from touching these spots.

        :param x: The current x position.
        :param y: The current y position.
        :return: A boolean of whether or not the x and y position are touching the markers.
        """
        if self.version > 1:
            return x in range(len(self.matrix) - 10 + 1, len(self.matrix) - 5 + 1) and y in range(
                len(self.matrix) - 10 + 1, len(self.matrix) - 5 + 1)

    def __in_fixed_area(self, x, y):
        """
        All QR codes have certain spots that contain other data not apart of the decryption. This includes error
        correction. This function will determine if this is within those fixed areas.

        :param x: The current x position.
        :param y: The current y position.
        :return: A boolean of whether the current position is in a fixed area.
        """
        if self.__within_orientation_markers(x, y):
            return True
        elif x == 6 or y == 6:
            return True

    def __decode_bits(self, traversal, start, number_of_bits=8):
        """
        This function decodes the bits. The starting value will correspond with the highest power of 2. This function
        will return the character generated from the bits.

        :param traversal: The traversal of the matrix.
        :param start: The starting index to decode.
        :param number_of_bits: The number of bits to generate a character. Currently set to one byte.
        :return: The string representation of the bits.
        """
        factor = 2 << (number_of_bits - 2)
        character = 0
        for i in traversal[start:start + number_of_bits]:
            character += i * factor
            if factor == 1:
                return character
            factor /= 2

    def __traverse_matrix(self):
        """
        This function will preform a zig-zag traversal over the demaksed matrix. It'll follow right to left until it
        reaches the top or bottom. Afterwards, it'll change direction (i.e. top to bottom). If it's out of bounds,
        it'll change direction. If it's in a fixed area, the coordinates will be ignored. Currently this is only set
        to traverse up till the 9th digit of the matrix.

        :return: A traversed list of values.
        """
        traversal = []
        x, y, direction = len(self.matrix) - 1, len(self.matrix) - 1, -1
        matrix = self.__demask()
        while True:
            if self.__out_of_bounds(x, y):
                direction, y, x = -direction, y - 2, x - direction
            if not self.__in_fixed_area(x, y):
                traversal += [matrix[x][y]]
            if y < 8:
                break
            elif y % 2 != 0:
                x, y = x + direction, y + 1
            else:
                y -= 1
        return traversal

    def __demask(self):
        """
        Removes the mask on the QR Matrix. This creates a matrix that has 1 represent black spots and 0 represent
        white spots, the opposite of the normal matrix. Also accounts for skipped row and column.

        :return: The unmasked QR Code
        """
        mask = self.__extract_mask_pattern()
        decoded_matrix = []
        y = 0
        while y < len(self.matrix):
            row = []
            x = 0
            while x < len(self.matrix[0]):
                modify_value = self.matrix[y][x]
                if modify_value == 255:
                    modify_value = 1
                row += [(~modify_value + 2 ^ ~mask[y][x] + 2)]
                x += 1
            decoded_matrix += [row]
            y += 1
        return decoded_matrix

    def encode(self):
        """
        Encodes the matrix.
        :return:
        """

        return

    def __extract_mask_pattern(self):
        """
        Find the mask pattern in the QR Code and returns the bit array representation of it. Remember that 255 is used
        to represent white and 0 is used to represet black. These 3 bits will correspond with a power of 2 to create
        a unique value. This will then be used to create a mask patter to decode things. Remember that row and column
        7 must be skipped because they are special. Last part needed to adjust for shift.

        :return: The mask pattern created.
        """

        mask_pattern = self.matrix[8][2:5]
        power = 1
        total = 0
        for i in mask_pattern:
            if i == 0:
                total += power
            power <<= 1
        mask_matrix = []
        j = 0
        for row in self.matrix:
            i = 0
            new_row = []
            for val in self.matrix[j]:
                if self.__extractMaskNumberBoolean(total, i, j):
                    new_row += [0]
                else:
                    new_row += [1]
                i += 1
            j += 1
            mask_matrix += [new_row]

        return mask_matrix

    def __extractMaskNumberBoolean(self, number, j, i):
        """
        The forumlas were copied inversely so the operands have been reversed in this function. This function
        returns a boolean that matches a certain pattern

        :param number: The mask pattern number.
        :param i: The x position.
        :param j: The y position.
        :return: The boolean of whether or not a spot should be inverted.
        """
        if number == 0:
            return (i * j) % 2 + (i * j) % 3 == 0
        elif number == 1:
            return i % 2 == 0
        elif number == 2:
            return ((i * j) % 3 + i + j) % 2 == 0
        elif number == 3:
            return (i + j) % 3 == 0
        elif number == 4:
            return (i // 2 + j // 3) % 2 == 0
        elif number == 5:
            return (i + j) % 2 == 0
        elif number == 6:
            return ((i * j) % 3 + i * j) % 2 == 0
        elif number == 7:
            return j % 3 == 0
        else:
            raise Exception("Unknown Mask Pattern")

    def __intify_matrix(self):
        """
        Make sure all elements are int.
        """

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                self.matrix[i][j] = int(self.matrix[i][j])

    def __extract_end_points(self, firstRow):
        """
        Extracts the dimensions of the matrix by utilizing the first row. This finds the first black spot and the last.

        :param firstRow: The first row with data.
        :return: A tuple of index of the first useful bit and the last useful bit.
        """
        wastedSpace = 0
        for num in firstRow:
            if num == 255:
                wastedSpace += 1
            else:
                break
        lastBlackIndex, count = wastedSpace, wastedSpace
        for num in firstRow[wastedSpace:]:
            if num == 0:
                lastBlackIndex = count
            count += 1
        return (wastedSpace, lastBlackIndex)

    def __rowIsWhiteSpace(self, row):
        """
        Returns a boolean of whether row is white space.

        :param row: A row of a matrix.
        :return: True if all white pixels, false otherwise.
        """
        for i in row:
            if i != 255:
                return False
        return True

    def __find_ratio(self, matrix):
        """
        Finds and returns the ratio of the image to it's 1 pixel per black pixel equivalent.

        :return: The scale of the matrix.
        """
        count = 0
        for num in matrix[0]:
            if int(num) == 255:
                return count // 7
            count += 1
        raise Exception("This image is not binary!")

    def __scale_matrix(self):
        """
        Scales the matrix to the smallest size possible

        :return: Nothing. This resizes the matrix.
        """
        ratio = self.__find_ratio(self.matrix)
        scaledMatrix = []
        yCount = 0
        for row in self.matrix:
            if yCount % ratio == 0:
                xCount = 0
                newRow = []
                for value in row:
                    if xCount % ratio == 0:
                        newRow += [value]
                    xCount += 1
                scaledMatrix += [newRow]
            yCount += 1
        self.matrix = scaledMatrix
