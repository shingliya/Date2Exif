import piexif

class ModifyPattern:
    MP_YYYYMMDD = 0
    MP_YYYYDDMM = 1
    MP_DDMMYYYY = 2
    MP_MMDDYYYY = 3
    MP_REMOVE = 4

class ErrorTypes:
    ET_wrong_file_type = 0
    ET_cant_open = 1
    ET_wrong_format = 2
    ET_sucess = 3

def loadImg(filepath: str, pattern: ModifyPattern = ModifyPattern.MP_YYYYMMDD) -> ErrorTypes:
    ext = filepath.split(".")[-1]
    if not (ext == "jpg" or ext == "jpeg"):
        return ErrorTypes.ET_wrong_file_type

    try:
        exif_dict = piexif.load(filepath)
    except:
        return ErrorTypes.ET_cant_open

    exif_ifd = exif_dict["Exif"]
    dateStr = ""

    if pattern != ModifyPattern.MP_REMOVE:
        dateStr = extractDate(filepath.split('/')[-1], pattern)

        if len(dateStr) == 0:
            return ErrorTypes.ET_wrong_format

    exif_ifd[piexif.ExifIFD.DateTimeOriginal] = exif_ifd[piexif.ExifIFD.DateTimeDigitized] = dateStr #"2021:09:29 23:0:10" example format
    
    try:
        exif_bytes = piexif.dump(exif_dict)
    except:
        del exif_dict["1st"]
        del exif_dict["thumbnail"]
        try:
            exif_bytes = piexif.dump(exif_dict)
        except:
            return ErrorTypes.ET_cant_open

    try: 
        piexif.insert(exif_bytes, filepath)
    except:
            return ErrorTypes.ET_cant_open

    return ErrorTypes.ET_sucess



def extractDate(filename: str, pattern: ModifyPattern = ModifyPattern.MP_YYYYMMDD) -> str:
    
    digits = [c for c in filename if c.isdigit()]

    if len(digits) < 8:
        return ""
        pass

    year = month = day = None

    if pattern == ModifyPattern.MP_YYYYMMDD:
        year =  int("".join(digits[0:4]))
        month = int("".join(digits[4:6]))
        day =   int("".join(digits[6:8]))
    elif pattern == ModifyPattern.MP_YYYYDDMM:
        year =  int("".join(digits[0:4]))
        month = int("".join(digits[6:8]))
        day =   int("".join(digits[4:6]))
    elif pattern == ModifyPattern.MP_DDMMYYYY:
        year =  int("".join(digits[4:8]))
        month = int("".join(digits[2:4]))
        day =   int("".join(digits[0:2]))
    elif pattern == ModifyPattern.MP_MMDDYYYY:
        year =  int("".join(digits[4:8]))
        month = int("".join(digits[0:2]))
        day =   int("".join(digits[2:4]))

    hours = "".join(digits[8:10])
    hours = min( int(hours if len(hours) > 0 else 0), 23 )

    minutes = "".join(digits[10:12])
    minutes = min( int(minutes if len(minutes) > 0 else 0), 59)

    seconds = "".join(digits[12:14])
    seconds = min( int(seconds if len(seconds) > 0 else 0), 59)

    return f"{year}:{month}:{day} {hours}:{minutes}:{seconds}"