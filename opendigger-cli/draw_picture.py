import json
import matplotlib.pyplot as plt

class picture:
    def __init__(self, name, xname, yname, data) -> None:
        self.name = name
        self.xlabel = xname
        self.ylabel = yname
        self.json_data = data

    def print_pic(self, path=None):
        # x_key = self.json_data.keys().replace("-", "")
        plt.bar(self.json_data.keys(), self.json_data.values())
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.xticks(rotation=90, fontsize=7)
        plt.suptitle(self.name)
        if path is not None:
            save_path = path
        else:
            save_path = "./picture.jpg"
        plt.savefig(save_path)

if __name__ == "__main__":
    with open('./test_json.json', 'r') as f:
        json_data = json.load(f)
    pic1 = picture('time', 'value', json_data)
    pic1.print_pic()