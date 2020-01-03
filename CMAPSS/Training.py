# -*- coding: utf-8 -*-
"""
AIAS ,Ryerson Univesity

Created on Tue Sep 17 12:19:06 2019

@author: 
    Tejas Janardhan
    AIAS Phd Student

"""

# =========================================================================================
# Choose an appropriate model to create and Train
# =========================================================================================

import tensorflow        as tf
tf.compat.v1.disable_eager_execution()
import matplotlib.pyplot as plt
import datetime

# class sGRUcell(tf.keras.layers.Layer):  #Stacked GRU
    
#     def __init__(self):
#       super(MyModel, self).__init__()

class RNN_to_FF:
        
    def __init__(self,
                 features,
                 rnn_neurons,
                 ff_neurons,
                 rnn_type     = 'simpleRNN',
                 epochs       = 10,
                 batch_size   = 32,
                 dropout      = 0.4,   #Dropout Probability
                 rec_dropout  = 0.2,
                 l2_k         = 0.001,
                 l2_b         = 0.,
                 l2_r         = 0., 
                 lRELU_alpha  = 0.05,
                 epsilon      = 1e-7,
                 lr           = 0.001,
                 beta         = [0.9,0.999],
                 model_dir      = None,
                 run_id         = None,
                 early_stopping = True,
                 enable_norm    = False):
      
    
        self.rnn_type    = rnn_type
        self.rnn_neurons = rnn_neurons
        self.ff_neurons  = ff_neurons
        
        self.features   = features
        self.epochs     = epochs 
        self.batch_size = batch_size
        
        self.dropout     = dropout
        self.rec_dropout = rec_dropout
        self.l2_k        = l2_k
        self.l2_r        = l2_r 
        self.l2_b        = l2_b  
        self.lr          = lr
        self.beta        = beta
        
        self.lRELU_alpha = lRELU_alpha
        self.epsilon     = epsilon
        
        self.model_dir      = model_dir 
        self.run_id         = run_id
        self.early_stopping = early_stopping
        self.enable_norm    = enable_norm
        
# ==================================================================================================
        
    def create_simpleRNN(self):
        
        for i in range(0, len(self.rnn_neurons)-1):
            
            self.model.add(tf.keras.layers.SimpleRNN(self.rnn_neurons[i],
                                                     dropout               = self.dropout,
                                                     recurrent_dropout     = self.rec_dropout,
                                                     kernel_regularizer    = self._l2_k,
                                                     bias_regularizer      = self._l2_b,
                                                     recurrent_regularizer = self._l2_r,
                                                     return_sequences=True))
            if self.enable_norm: self.model.add(tf.keras.layers.LayerNormalization())
    
        self.model.add(tf.keras.layers.SimpleRNN(self.rnn_neurons[-1],
                                                 dropout               = self.dropout,
                                                 recurrent_dropout     = self.rec_dropout,
                                                 kernel_regularizer    = self._l2_k,
                                                 bias_regularizer      = self._l2_b,
                                                 recurrent_regularizer = self._l2_r))
        if self.enable_norm: self.model.add(tf.keras.layers.LayerNormalization())
        
# ==================================================================================================        
        
    def create_LSTM(self):

        for i in range(0, len(self.rnn_neurons)-1):
            
            self.model.add(tf.keras.layers.LSTM(self.rnn_neurons[i],
                                                dropout               = self.dropout,
                                                recurrent_dropout     = self.rec_dropout,
                                                kernel_regularizer    = self._l2_k,
                                                bias_regularizer      = self._l2_b,
                                                recurrent_regularizer = self._l2_r,
                                                return_sequences=True))
            if self.enable_norm: self.model.add(tf.keras.layers.LayerNormalization())
    
        self.model.add(tf.keras.layers.LSTM(self.rnn_neurons[-1],
                                            dropout               = self.dropout,
                                            recurrent_dropout     = self.rec_dropout,
                                            kernel_regularizer    = self._l2_k,
                                            bias_regularizer      = self._l2_b,
                                            recurrent_regularizer = self._l2_r))
        if self.enable_norm: self.model.add(tf.keras.layers.LayerNormalization())
        
# ==================================================================================================          

    def create_GRU(self):

        
# ==================================================================================================        
    
    def create_model(self):
        
        self.model   = tf.keras.Sequential(tf.keras.layers.Masking(mask_value = 1000.0,
                                                                   input_shape=(None,self.features)))
        self._l2_k = tf.keras.regularizers.l2(l=self.l2_k)
        self._l2_r = tf.keras.regularizers.l2(l=self.l2_r)
        self._l2_b = tf.keras.regularizers.l2(l=self.l2_b)
        
        if self.rnn_type == 'simpleRNN':
            self.create_simpleRNN()
        elif self.rnn_type == 'LSTM':
            self.create_LSTM()
        else:
            raise Exception('Invalid RNN Type, choose between simpleRNN or LSTM')

        for i in range(0, len(self.ff_neurons)):
            
            self.model.add(tf.keras.layers.Dense(self.ff_neurons[i],
                                                 kernel_regularizer = self._l2_k,
                                                 bias_regularizer   = self._l2_b))
            
            self.model.add(tf.keras.layers.LeakyReLU())
            if self.enable_norm: self.model.add(tf.keras.layers.BatchNormalization())
       
        #Final Layer
        self.model.add(tf.keras.layers.Dense(1,
                                             activation = 'softplus'))
        
        optimizer = tf.keras.optimizers.Adam(learning_rate = self.lr,
                                             beta_1        = self.beta[0],
                                             beta_2        = self.beta[1],
                                             epsilon       = self.epsilon)
        
        def seq_loss(true, pred):
            
            return tf.keras.backend.mean((true-pred)**2)
        
        self.model.compile(loss='mse',
                           optimizer = optimizer)
        
        print(self.model.summary())
        
# ================================================================================================
        
    def train_model(self,
                    train_in, 
                    train_out,
                    val_in,
                    val_out):
        
        t_stamp = datetime.datetime.now()
        t_stamp = t_stamp.strftime('%d_%b_%y__%H_%M')
        
        if self.early_stopping == True:
            
            callbacks = [tf.keras.callbacks.EarlyStopping(monitor  = 'val_loss', 
                                                          patience = 50,
                                                          restore_best_weights = True)]
        else:
            callbacks = []
       
        
        self.h = self.model.fit(train_in,
                                train_out,
                                validation_data = (val_in, val_out),
                                epochs          = self.epochs,
                                shuffle         = True,
                                callbacks       = callbacks)
                
        self.loss     = int(round(self.h.history['loss'][-1]))
        self.val_loss = int(round(self.h.history['val_loss'][-1]))
        
        if self.run_id != None:
            
            self.model.save_weights(self.model_dir + '/' + self.run_id + '.h5')
            model_json = self.model.to_json()
            
            with open(self.model_dir + '/' + self.run_id + '.json', "w") as json_file:
                json_file.write(model_json)
             
# ================================================================================================

    def history_plot(self):
                    
        plt.plot(self.h.history['loss'])
        plt.plot(self.h.history['val_loss'])
        plt.title('Model Loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper left')
        plt.show()
        
# ================================================================================================== 
# ==================================================================================================
