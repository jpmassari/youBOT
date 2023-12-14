import os

def clear_folders():
  folder_path = ["./upload", "./content"] #self.getParam()
  for folder in folder_path:
    for file_name in os.listdir(folder):
      file_path = os.path.join(folder, file_name)
      if os.path.isfile(file_path):
        os.remove(file_path)