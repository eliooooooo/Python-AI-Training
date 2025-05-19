#### Imports
import pickle
import gzip
from PIL import Image
import numpy as np
import random
import time

# Lecture des données dans le fichier pkl.gz
def load_data():
    f = gzip.open('./mnist.pkl.gz', 'rb')
    u = pickle._Unpickler(f)
    u.encoding = 'latin1'
    training_data, validation_data, test_data = u.load()
    f.close()
    return (training_data, validation_data, test_data)

# Conversion des données en tableaux numpy
def load_data_wrapper():
    tr_d, va_d, te_d = load_data()
    training_inputs = [np.reshape(x, (784, 1)) for x in tr_d[0]]
    training_results = [vectorized_result(y) for y in tr_d[1]]
    training_data = list(zip(training_inputs, training_results))
    validation_inputs = [np.reshape(x, (784, 1)) for x in va_d[0]]
    validation_data = list(zip(validation_inputs, va_d[1]))
    test_inputs = [np.reshape(x, (784, 1)) for x in te_d[0]]
    test_data = list(zip(test_inputs, te_d[1]))

    return (training_data, validation_data, test_data)

# Conversion d'un résultat (entre 0 et 9) en vecteur
# Ex: 1 -> [0,1,0,0,0,0,0,0,0,0]
def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

# Convertit les données en images (pour visualiser les données utilisées)
def convert_to_images():
    tr_d, va_d, te_d = load_data()
    training_inputs = [np.reshape(x, (784, 1)) for x in tr_d[0]]
    training_results = [vectorized_result(y) for y in tr_d[1]]
    validation_inputs = [np.reshape(x, (784, 1)) for x in va_d[0]]
    test_inputs = [np.reshape(x, (784, 1)) for x in te_d[0]]

    for i in range(len(training_inputs)):
        image = Image.fromarray((training_inputs[i].reshape(28,28)*256).astype(np.uint8), mode='L')
        image.save('./data/training/'+str(i)+'.png')

    for i in range(len(validation_inputs)):
        image = Image.fromarray((training_inputs[i].reshape(28,28)*256).astype(np.uint8), mode='L')
        image.save('./data/validation/'+str(i)+'.png')

    for i in range(len(test_inputs)):
        image = Image.fromarray((training_inputs[i].reshape(28,28)*256).astype(np.uint8), mode='L')
        image.save('./data/test/'+str(i)+'.png')

#############################################
##### Classe pour le réseau de neurones #####
#############################################
class Network(object):
    # Intialise le réseau
    def __init__(self, sizes):
        """The list ``sizes`` contains the number of neurons in the
        respective layers of the network.  For example, if the list
        was [2, 3, 1] then it would be a three-layer network, with the
        first layer containing 2 neurons, the second layer 3 neurons,
        and the third layer 1 neuron.  The biases and weights for the
        network are initialized randomly, using a Gaussian
        distribution with mean 0, and variance 1.  Note that the first
        layer is assumed to be an input layer, and by convention we
        won't set any biases for those neurons, since biases are only
        ever used in computing the outputs from later layers."""
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(sizes[:-1], sizes[1:])]

    # Propage de l'input vers l'output
    def feedforward(self, a):
        """Return the output of the network if ``a`` is input."""
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a)+b)
        return a

    # Entrainement du réseau
    def SGD(self, training_data, epochs, mini_batch_size, eta,
            test_data=None):
        """Train the neural network using mini-batch stochastic
        gradient descent.  The ``training_data`` is a list of tuples
        ``(x, y)`` representing the training inputs and the desired
        outputs.  The other non-optional parameters are
        self-explanatory.  If ``test_data`` is provided then the
        network will be evaluated against the test data after each
        epoch, and partial progress printed out.  This is useful for
        tracking progress, but slows things down substantially."""
        if test_data: n_test = len(test_data)
        n = len(training_data)
        for j in range(epochs):
            time1 = time.time()
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)
            time2 = time.time()
            if test_data:
                print("Epoch {0}: {1} / {2}, took {3:.2f} seconds".format(
                    j, self.evaluate(test_data), n_test, time2-time1))
            else:
                print("Epoch {0} complete in {1:.2f} seconds".format(j, time2-time1))

    # Met à jour le réseau
    def update_mini_batch(self, mini_batch, eta):
        """Update the network's weights and biases by applying
        gradient descent using backpropagation to a single mini batch.
        The ``mini_batch`` is a list of tuples ``(x, y)``, and ``eta``
        is the learning rate."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw
                        for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb
                       for b, nb in zip(self.biases, nabla_b)]

    # Propagation de l'erreur de l'output vers l'input
    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x]
        zs = []  # liste pour stocker tous les vecteurs z, couche par couche
        
        # Propagation avant (feedforward)
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        
        # Propagation arrière (backward pass)
        delta = self.cost_derivative(activations[-1], y) * sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        
        # Note: l = 1 signifie la dernière couche, l = 2 l'avant-dernière, etc.
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        
        return (nabla_b, nabla_w)
            
        
    # Evalue la performance du réseau
    def evaluate(self, test_data):
        """Return the number of test inputs for which the neural
        network outputs the correct result. Note that the neural
        network's output is assumed to be the index of whichever
        neuron in the final layer has the highest activation."""
        test_results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    # Calcul d'erreur
    def cost_derivative(self, output_activations, y):
        """Return the vector of partial derivatives \partial C_x /
        \partial a for the output activations."""
        return (output_activations-y)

#### Miscellaneous functions
def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
    """Derivative of the sigmoid function."""
    return sigmoid(z)*(1-sigmoid(z))


# @TODO: Décommenter la ligne suivante pour convertir les données en images
# convert_to_images()

training_data, validation_data, test_data = load_data_wrapper()

net = Network([784, 30, 10])

net.SGD(training_data, 30, 10, 3.0, test_data=test_data)

########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
#####       _______  __   __  ___     ______   _______    _______  _______  _______  _______       #####
#####      |       ||  | |  ||   |   |      | |       |  |       ||       ||       ||       |      #####
#####      |    ___||  | |  ||   |   |  _    ||    ___|  |_     _||    ___||  _____||_     _|      #####
#####      |   | __ |  |_|  ||   |   | | |   ||   |___     |   |  |   |___ | |_____   |   |        #####
#####      |   ||  ||       ||   |   | |_|   ||    ___|    |   |  |    ___||_____  |  |   |        #####
#####      |   |_| ||       ||   |   |       ||   |___     |   |  |   |___  _____| |  |   |        #####
#####      |_______||_______||___|   |______| |_______|    |___|  |_______||_______|  |___|        #####
#####                                                                                              #####
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
from tkinter import *
import tkinter.messagebox as tmsg 
from PIL import Image, ImageDraw
import numpy as np

# Starting point of mouse dragging or shapes
prev_x = 0 
prev_y = 0 
# Current x,y position of mouse cursor or end position of dragging
x = 0 
y = 0
created_element_info = [] #list of all shapes objects for saving drawing
new = [] # Each shapes of canvas
created = [] # Temporary list to hold info on every drag
shape = "Line" # Shape to draw
color = "black" # Color of the shape
line_width = 15 # Width of the line shape

converted = ""
converted_info = ""

# Update the previous position on mouse left click
def drawOnePixel(e=""):
    global x,y
    try:
        # Update current Position
        x = e.x
        y = e.y

        #Generate Element
        element = createElms()
        deleteUnwanted(element) # Delete unwanted shapes
        generateShapesObj()
    except Exception as e:
        tmsg.showerror("Some Error Occurred!", e)

# After Every drawing create info of drawing and add the element to new list and assign empty list to created
def generateShapesObj(e=""):
    global created,created_element_info
    new.append(created[-1])
    created = []
    created_element_info_obj = {
        "type": shape,
        "color": color,
        "prev_x": prev_x,
        "prev_y": prev_y,
        "x": x,
        "y": y
    }
    created_element_info.append(created_element_info_obj)

# Create Elements on canvas based on shape variable
def createElms():
    a = canvas.create_line(x, y, x+1, y,
                            width=line_width, fill=color,
                            capstyle=ROUND, smooth=TRUE, splinesteps=3)
    draw.ellipse((x-line_width/2,y-line_width/2,x+line_width/2,y+line_width/2),fill="white")
    return a


def deleteUnwanted(element):
    global created
    created.append(element) #Elements that created
    for item in created[:-1]: 
        canvas.delete(item)

# Convert to digit
def convert():
    global converted, converted_info

    a = np.asarray(image1.convert('L').resize((28,28)))

    image = Image.fromarray(a, mode='L')
    
    image1.save('Reseau_Neurones/converted.png')
    image.save('Reseau_Neurones/converted_resize.png')

    a = a.astype(np.float32).reshape((784,1))
    res = net.feedforward(a)
    converted = str(np.argmax(res)) + " ("

    for i in range(0,10):
        converted = converted + str(i) + ": " + str(res[i]*100) + "%; "

    status.set(converted + ")")

# Clear the Canvas
def clearCanvas(e=""):
    global created_element_info, canvas, created, new, converted, converted_info, image1, draw
    canvas.delete("all")
    created_element_info = []
    created = []
    new = []
    converted = ""
    converted_info = ""

    image1 = Image.new("RGB", (CANVAS_WIDTH, CANVAS_WIDTH), "black")
    draw = ImageDraw.Draw(image1)

root = Tk()
root.title("Drawing Pad")
root.minsize(280,280) #Minimum Size of the window
# All Widgets here such as canvas, buttons etc

# Canvas
CANVAS_WIDTH = 280
CANVAS_HEIGHT = 280
canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

image1 = Image.new("RGB", (CANVAS_WIDTH, CANVAS_WIDTH), "black")
draw = ImageDraw.Draw(image1)

# Binding Events to canvas
# Structure: canvas.bind("<eventcodename>", function-name)
canvas.bind("<1>", drawOnePixel) #On Mouse left click
canvas.bind("<B1-Motion>", drawOnePixel) #Capture Mouse left click + move (dragging)
frame = Frame(root)
frame.pack(side=BOTTOM)
radiovalue = StringVar()
radiovalue.set("Line") #Default Select

#Buttons
Button(frame, text="Clear", font="comicsans 12 bold",
       command=clearCanvas).pack(side=BOTTOM, padx=6)
Button(frame, text="Convert", font="comicsans 12 bold",
       command=convert).pack(side=BOTTOM, padx=6)

# Status Bar
status = StringVar()
status.set(converted)
statusbar = Label(root, textvariable=status, anchor="w", relief=SUNKEN)
statusbar.pack(side=BOTTOM, fill=X)

root.mainloop()
