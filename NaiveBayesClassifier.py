import csv
import math
import random
import sys

class NaiveBayesClassifier:
    
    def __init__(self):
        args = sys.argv
        self.vocabulary_file = "20newsgroups/vocabulary.txt"
        self.categories_file = "20newsgroups/map.csv"
        self.train_label_file = "20newsgroups/train_label.csv"
        self.train_data_file = "20newsgroups/train_data.csv"
        self.test_label_file = "20newsgroups/test_label.csv"
        self.test_data_file = "20newsgroups/test_data.csv"

        if args!=None and len(args)==7:
            self.vocabulary_file = args[1]
            self.categories_file = args[2]
            self.train_label_file = args[3]
            self.train_data_file = args[4]
            self.test_label_file = args[5]
            self.test_data_file = args[6]

        #Initialize prior counts - (<categoryID>, count)
        self.categories_count = dict()

        #Maintain priors as (categoryID, p(omega))
        self.priors = dict()

        #Maintain labelled documents and categories
        self.docs_labels = dict()

        #Maintain categories and number of words
        self.num_words = dict()

        #Maintains, for each word X category - number of words in category
        self.all_words_by_category = dict()

        #Construct a Document Index - tells which words are in document <docId, [word1, word2]>
        self.document_index = dict()

        #Read the test data into file
        self.boo=True

        #Initialize a dictionary to maintain vocabulary (word_ID, boolean)
        self.vocabulary = dict()

    def read_categories(self):
        self.categories = dict()
        with open(self.categories_file, 'rb') as categories:
            categories_reader = csv.reader(categories, delimiter = ",")
            for row in categories_reader:
                self.categories[row[0]] = row[1]

    def read_training_data(self):
        with open(self.train_data_file, 'rb') as train_data:
            train_data_reader = csv.reader(train_data, delimiter = ",")

    def read_test_data(self):
        categories_count = dict()
        test_document_index = dict()
        with open(self.test_data_file, 'rb') as test_data:
            test_data_reader = csv.reader(test_data, delimiter = ",")
            for row in test_data_reader:
                word_id = row[1]
                doc_id = row[0]
                words = test_document_index.get(doc_id, set())
                words.add(word_id)
                test_document_index[doc_id] = words

        test_labels = dict()
        with open(self.test_label_file, 'rb') as test_label:
            labelled_docs = csv.reader(test_label)
            doc_number = 0
            for row in labelled_docs:
                category_id = row[0]
                test_labels[str(doc_number+1)] = category_id
                doc_number+=1
                c = categories_count.get(category_id, 0)
                c+=1
                categories_count[category_id] = c

        return test_document_index, test_labels, categories_count

    def estimate_priors(self):
        total_docs = 0
        with open(self.train_label_file, 'rb') as train_label:
            labelled_docs = csv.reader(train_label)
    
            for row in labelled_docs:
                self.update_category_count(row[0])
                self.docs_labels[str(total_docs+1)] = row[0]
                total_docs+=1
    
        for key, value in self.categories_count.iteritems():
            self.priors[key] = float(value)/float(total_docs)
        
    def calculate_total_words(self):
        with open(self.train_data_file, 'rb') as train_data:
            train_data_reader = csv.reader(train_data, delimiter = ",")
            for row in train_data_reader:
                category_id = self.docs_labels[row[0]]
                self.update_word_count(category_id, int(row[2]))
                self.update_word_by_category(row[1], category_id, int(row[2]))
                self.update_document_index(row[0], row[1]) 
    
    # |Vocabulary|
    def calculate_vocabulary_count(self):
        with open(self.vocabulary_file, 'rb') as vocabulary:
            reader = csv.reader(vocabulary)
            c = 0
            for row in reader:
                c+=1
                self.vocabulary[str(c)] = True
            self.vocabular_size = c

    #Update doc words
    def update_document_index(self, doc_id, word_id):
        words = self.document_index.get(doc_id, set())
        words.add(word_id)
        self.document_index[doc_id] = words

    # Increment the number of documents for category_id
    def update_category_count(self, category_id):
        count = self.categories_count.get(category_id, 0)
        count+=1
        self.categories_count[category_id] = count

    #Increment the number of words for category_id by n_words
    def update_word_count(self, category_id, n_words):
        c = self.num_words.get(category_id, 0)
        c+=n_words
        self.num_words[category_id] = c

    #Calculate for each word, number of times it appears in category
    def update_word_by_category(self, word_id, category_id, n):
        category_frequency = self.all_words_by_category.get(word_id, dict())
        f = category_frequency.get(category_id, 0)
        f+=n
        category_frequency[category_id] = f
        self.all_words_by_category[word_id] = category_frequency

    def n_k(self, word_id, category_id):
        word_frequencies = self.all_words_by_category.get(word_id, dict())
        f = word_frequencies.get(category_id, 0)
        return f

    # Calculate Maximum Likelihood estimation
    def mle(self, word_id, category_id):
        n_k = self.n_k(word_id, category_id)
        n = self.num_words[category_id]
        return float(n_k)/float(n)

    # Calculate Bayesian estimation
    def be(self, word_id, category_id):
        n_k = self.n_k(word_id, category_id)
        n = self.num_words[category_id]
        return float(n_k+1)/ float(n+self.vocabular_size)

    # Print the priors
    def print_priors(self):
        print 'Priors:'
        keys = sorted(self.priors.keys(), cmp = self.category_comparator)
        for key in keys:
            print "P(Omega = {}) = {}".format(key, self.priors[key])
        print

    # comparator to print
    def category_comparator(self, c_1, c_2):
        if(int(c_1) < int(c_2)):
            return -1
        elif(int(c_1) > int(c_2)):
            return 1
        else: 
            return 0

    # Print some MLE, BE for report
    def print_estimates(self):
        for x in xrange(1,10):
            for y in xrange(1,10):
                print "MLE {} BE {}".format(self.mle(str(x),str(y)), self.be(str(x),str(y)))

    def classify(self, document_index, doc_id,estimator):
        max_j = float('-inf')
        classification = None
        for category in self.categories_count.keys():
            prior = math.log(self.priors[category])
            p = prior
            word_not_in_category = False
            for w in document_index[doc_id]:
                if(self.vocabulary.get(w)==None):
                    #It's a new word
                    continue
                e = estimator(w, category)
                if(e!=0):
                    p+= math.log(e)
                else:
                    #TODO: Check vocabulary if it exists and then set to true. either way ensure in the function that some classification is returned.        
                    word_not_in_category = True
                    break
            if(word_not_in_category):
                continue
            if(p>max_j):
                max_j = p
                classification = category

        if(classification==None):
            classification = random.choice(self.categories_count.keys())
        return classification

    def create_confusion_matrix(self):
        c = len(self.categories_count.keys())
        return [[0 for x in range(c)] for y in range(c)]

    def print_confusion_matrix(self, m):
        c = len(self.categories_count.keys())
        for i in range(c):
            for j in range(c):
                print "%03d " % (m[i][j]), 
            print ''


    def compute_accuracy_data(self, document_index, labelled_data, estimator, categories_count):
        category_classification = dict()
        confusion_matrix = self.create_confusion_matrix()
        total_docs = len(labelled_data.keys())
        correct = 0
        i = 0
        for doc_id, category_id in labelled_data.iteritems():
            classification_id = self.classify(document_index, doc_id, estimator)
            if(classification_id==category_id):
                correct+=1
                c_frequency = category_classification.get(category_id, 0)
                c_frequency+=1
                category_classification[category_id] = c_frequency
            if(classification_id==None):
                continue
            confusion_matrix[int(category_id)-1][int(classification_id)-1] +=1

        accuracy = float(correct)/float(total_docs)

        print "Overall Accuracy = " + str(accuracy)

        #Compute category accuracy
        categories = sorted(categories_count.keys(), cmp = self.category_comparator)
        a = 0
        b = 0
        for category_id in categories:
            classifications_made = category_classification.get(category_id,0)
            total = categories_count[category_id]
            acc = float(classifications_made)/float(total)
            a+=classifications_made
            b+=total
            print "Group {}: {}".format(category_id, acc)
        print "Confusion Matrix:"
        self.print_confusion_matrix(confusion_matrix)

    def compute_accuracy(self):
        self.print_priors()
        print "Train Data with BE"
        self.compute_accuracy_data(self.document_index, self.docs_labels, self.be, self.categories_count)
        
        #Do it on test data now
        test_document_index, test_labels, test_data_categories_count = self.read_test_data()
        print "Test Data with MLE"
        self.compute_accuracy_data(test_document_index, test_labels, self.mle, test_data_categories_count)
        print
        print "Test Data with BE"
        self.compute_accuracy_data(test_document_index, test_labels, self.be, test_data_categories_count)


n = NaiveBayesClassifier()
n.read_categories()
n.read_training_data()
n.estimate_priors()
n.calculate_total_words()
n.calculate_vocabulary_count()
n.compute_accuracy()