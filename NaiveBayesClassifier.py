import csv

class NaiveBayesClassifier:
    
    def __init__(self):
        self.categories_file = "20newsgroups/map.csv"
        self.train_data_file = "20newsgroups/train_data.csv"
        self.train_label_file = "20newsgroups/train_label.csv"

        #Initialize prior counts - (<categoriID>, count)
        self.categories_count = dict()
        self.priors = dict()

    def read_categories(self):
        self.categories = dict()
        with open(self.categories_file, 'rb') as categories:
            categories_reader = csv.reader(categories, delimiter = ",")
            for row in categories_reader:
                self.categories[row[0]] = row[1]

    def read_training_data(self):
        with open(self.train_data_file, 'rb') as train_data:
            train_data_reader = csv.reader(train_data, delimiter = ",")


    def estimate_priors(self):
        total_docs = 0
        with open(self.train_label_file, 'rb') as train_label:
            labelled_docs = csv.reader(train_label)
    
            for row in labelled_docs:
                self.update_category_count(row[0])
                total_docs+=1
    
        for key, value in self.categories_count.iteritems():
            self.priors[key] = float(value)/float(total_docs)
        

    def update_category_count(self, category_id):
        count = self.categories_count.get(category_id, 0)
        count+=1
        self.categories_count[category_id] = count



n = NaiveBayesClassifier()
n.read_categories()
n.read_training_data()
n.estimate_priors()
