import os
import shutil
import zipfile
from pymkv import MKVFile, MKVTrack
from pathlib import Path
import py7zr

# Global Variable
DELETE_FONTS = True
DELETE_ORIGINAL_MKV = False
RENAME_ORIGINAL_MKV = True
DELETE_ORIGINAL_MKA = False
RENAME_ORIGINAL_MKA = True
DELETE_CHS_SUB = False
RENAME_CHS_SUB = True
DELETE_CHT_SUB = False
RENAME_CHT_SUB = True
SUFFIX_NAME = "_Plex"


# https://gist.github.com/hideaki-t/c42a16189dd5f88a955d
def unzip(f, encoding):
    font_list = []
    with zipfile.ZipFile(f) as z:
        for i in z.namelist():
            font_list.append("Fonts/" + i.encode('cp437').decode(encoding))
            n = Path("Fonts/" + i.encode('cp437').decode(encoding))
            if i[-1] == '/':
                if not n.exists():
                    n.mkdir()
            else:
                with n.open('wb') as w:
                    w.write(z.read(i))
    return font_list


if __name__ == '__main__':
    if DELETE_ORIGINAL_MKV and RENAME_ORIGINAL_MKV:
        print("Rename MKV instead")
        DELETE_ORIGINAL_MKV = False
    if DELETE_ORIGINAL_MKA and RENAME_ORIGINAL_MKA:
        print("Rename MKA instead")
        DELETE_ORIGINAL_MKA = False
    if DELETE_CHS_SUB and RENAME_CHS_SUB:
        print("Rename CHS instead")
        DELETE_ORIGINAL_MKA = False
    if DELETE_CHT_SUB and RENAME_CHT_SUB:
        print("Rename CHT instead")
        DELETE_ORIGINAL_MKA = False
    delete_list = []
    rename_list = []

    # A useful global variable
    folder_list = os.listdir()

    # Prepare fonts
    font_list = []
    if os.path.exists("Fonts"):
        font_list = os.listdir("Fonts")
        print("Loading fonts: " + str(font_list))
    else:
        for file_name in folder_list:
            if "Font" in file_name and ".zip" in file_name:
                print("Find font package file: " + file_name)
                if not os.path.exists("Fonts"):
                    os.makedirs("Fonts")
                    print("Fonts sub-directory created")
                font_list = unzip(file_name, "GBK")
                print("Unzipped to /Fonts: " + str(font_list))
                print("=" * 20)
            elif "Font" in file_name and ".7z" in file_name:
                print("Find font package file: " + file_name)
                if not os.path.exists("Fonts"):
                    os.makedirs("Fonts")
                    print("Fonts sub-directory created")
                with py7zr.SevenZipFile(file_name, mode='r') as z:
                    z.extractall("Fonts")
                    font_list = z.getnames()
                    print("Unzipped to /Fonts: " + str(font_list))
            else:
                pass
    #input("waiting....")
    # Main tasks
    for file_name in folder_list:
        skip_this_task = True
        if ".mkv" in file_name:
            episode_name = file_name.replace(".mkv", "")
            this_task = MKVFile(file_name)
            for item in folder_list:
                if episode_name in item:
                    if ".mkv" in item:
                        print("Find main video: " + item)
                        if DELETE_ORIGINAL_MKV:
                            delete_list.append(item)
                        if RENAME_ORIGINAL_MKV:
                            rename_list.append(item)
                    if ".ass" in item:
                        skip_this_task = False
                        if "chs" in item.lower() or "sc" in item.lower() or "jpsc" in item.lower():
                            this_chs = MKVTrack(item, track_name="chs", default_track=True, language="chi")
                            this_task.add_track(this_chs)
                            print("Find associated CHS subtitle: " + item)
                            if DELETE_CHS_SUB:
                                delete_list.append(item)
                            if RENAME_CHS_SUB:
                                rename_list.append(item)
                        if "cht" in item.lower() or "tc" in item.lower() or "jptc" in item.lower():
                            this_cht = MKVTrack(item, track_name="cht", default_track=False, language="chi")
                            this_task.add_track(this_cht)
                            print("Find associated CHT subtitle: " + item)
                            if DELETE_CHT_SUB:
                                delete_list.append(item)
                            if RENAME_CHT_SUB:
                                rename_list.append(item)
                    if ".mka" in item:
                        skip_this_task = False
                        this_task.add_track(item)
                        print("Find associated audio: " + item)
                        if DELETE_ORIGINAL_MKA:
                            delete_list.append(item)
                        if RENAME_ORIGINAL_MKA:
                            rename_list.append(item)
            for font in font_list:
                font = "Fonts/" + font
                this_task.add_attachment(font)
            if not skip_this_task:
                newMKV_name = episode_name + SUFFIX_NAME + ".mkv"
                this_task.mux(newMKV_name)
                print("=" * 20)
            else:
                print("No task for this MKV")

    # Clean up
    ## 创建Extra目录
    ExtraFolderIsExists = os.path.exists("Extra")
    if not ExtraFolderIsExists:
        os.makedirs("Extra")
    try:
        shutil.rmtree("Fonts/")
        print("Remove Fonts Folder Successfully")
    except:
        print("Remove Fonts Folder Error")
    for file in delete_list:
        try:
            os.remove(file)
        except:
            print("Failed to delete " + file)
    for file in rename_list:
        # os.rename(file, file + ".bak")
        shutil.move(file, "Extra/"+file)

    input("Task finished. Press Enter to exit...")
