import os
import re
import shutil
import time


def in_folder(folders, image):
    folder_name = ''.join(folder_name_from_image([image]))
    if folder_name in folders:
        return folder_name
    else:
        return folders[-1]


def truncate_folders_name(fold):
    fold = fold.lower()
    fold = fold.split('plur')[0].strip()
    return fold


def folder_name_from_image(image_names):
    # removing_illegal characters
    images = list(
        map(lambda x: "".join(re.findall("-[A-Z|a-z _-]+", x)), image_names))
    # generating folder names from images names
    folders = [truncate_folders_name((x[1:]).strip()) for x in sorted(set(images))]
    if '' in folders:
        folders.remove("")
    return folders


def make_structured_images(images_path, output_path, extra_folder_name='extras'):
    # option to make it load previous data and option form run from start

    # creating output folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # all images in the folder
    imgs = os.listdir(images_path)

    # generating folder_names
    folders = folder_name_from_image(imgs)

    folders.append(extra_folder_name)
    # getting previously saved_files
    folder_images = {}
    for i in folders:
        if not os.path.exists(f"{output_path}/{i}"):
            os.makedirs(f"{output_path}/{i}")
        folder_images[i] = os.listdir(f"{output_path}/{i}")

    for i in imgs:
        folder = in_folder(folders, i.lower())
        # only saving new files
        if i not in folder_images[folder]:
            shutil.copy(f"{images_path}/{i}", f"{output_path}/{folder}/{i}")

    print(f'images={len(imgs):,} folders={len(os.listdir(output_path)):,}')
if __name__ == '__main__':
    make_structured_images("D://Programming/SCREENSHOTS", 'D://Programming/STRUCTURED_SCREENSHOTS')