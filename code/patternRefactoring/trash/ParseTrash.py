# patternRefactoring/trash/ParseTrash.py
# Parse file contents into Trash objects,
# placing each into a Fillable holder.

class ParseTrash:
    def fillBin(String filename, Fillable bin):
        for line in open(filename).readlines():
            String type = line.substring(0,
              line.index(':')).strip()
            weight = Double.valueOf(
              line.substring(line.index(':') + 1)
                .strip()).doubleValue()
            bin.addTrash(
              Trash.factory(
                Trash.Messenger(type, weight)))

    # Special case to handle Collection:
    def fillBin(String filename, Bin):
        fillBin(filename, FillableCollection(bin))