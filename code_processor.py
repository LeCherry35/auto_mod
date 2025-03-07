import os
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models

class CodeProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_PATH"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return None

    
    def make_code_description(self, file_content):
        
        response = self.client.create_completion(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a developer who analyzes provided code and describes what is it desined for. Dont give sugesstions or improvements, just describe the code."}, {"role": "user", "content": file_content}],
            max_tokens=100
        )
        return response.choices[0].message['content']

    def save_point(self, collection_name, filename, file_content, description, embedding):
        point_id = uuid.uuid4().int & ((1 << 64) - 1)
        self.qdrant_client.upsert(
            collection_name=collection_name,
            points=[models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    filename: filename,
                    file_content: file_content,
                    description: description,
                }
            )]
        )
    
    def process_folder(self, folder_path, collection_name):
        
        output_dir = "output_files"  # Change this to your desired output directory

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_contents = []
        
        if not os.path.exists(folder_path):
            print(f"Папка '{folder_path}' не существует.")
            return file_contents
        
        for plugin_folder in os.listdir(folder_path):
            # print(f"{plugin_folder}")
            plugin_contents = ""
            for root, _, files in os.walk(os.path.join(folder_path, plugin_folder)):  # Recursively walk through directories
                print(f"{files}")
                for filename in files:
                    print(f"{filename}")
                    file_path = os.path.join(root, filename)
                    try:
                        file_content = self.read_file(file_path)
                        file_content = f"{filename}/n/n{file_content}"
                        plugin_contents += file_content
                    except Exception as e:
                        print(f"Ошибка при чтении файла {file_path}: {e}")
            output_file_path = os.path.join(output_dir, f"{plugin_folder}_contents.txt")
        
            # Write the contents to the output file
            try:
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(plugin_contents)
                print(f"Contents of {plugin_folder} saved to {output_file_path}")
            except Exception as e:
                print(f"Error writing to file {output_file_path}: {e}")
        #     file_path = os.path.join(folder_path, filename)
            
        #     if os.path.isfile(file_path):
        #         try:
        #             file_content = self.read_file(file_path)
        #             description = self.make_code_description(file_content)
        #             embedding = self.client.embeddings.create(
        #             model="text-embedding-3-small",
        #             input=description
        #             )
        #             file_contents.append((filename, file_content, description, embedding))
        #         except Exception as e:
        #             print(f"Ошибка при чтении файла {filename} и создния описания: {e}")
                    
        # if not self.qdrant_client.collection_exists(collection_name):
        #     self.qdrant_client.create_collection(
        #         collection_name=collection_name,
        #         vectors_config=models.VectorParams(
        #             size=1536,
        #             distance=models.Distance.COSINE
        #         )
        #     )
        # for data in file_contents:
        #     filename, file_content, description, embedding = data
        #     self.save_point(collection_name, filename, file_content, description, embedding)
        #     print(f"Файл {filename} успешно сохранен в бд {collection_name}.")
            
pr = CodeProcessor()

pr.process_folder("code", "F")   