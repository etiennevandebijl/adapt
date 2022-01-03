"""
DANN
"""

import numpy as np
import tensorflow as tf

from adapt.base import BaseAdaptDeep, make_insert_doc
from adapt.utils import check_network

EPS = np.finfo(np.float32).eps


@make_insert_doc(["encoder", "task"])
class MDD(BaseAdaptDeep):
    """
    MDD: Margin Disparity Discrepancy is a feature-based domain adaptation
    method originally introduced for unsupervised classification DA.
    
    The goal of MDD is to find a new representation of the input features which
    minimizes the disparity discrepancy between the source and target domains 
    
    The discrepancy is estimated through adversarial training of three networks:
    An encoder a task network and a discriminator.
    
    Parameters
    ----------
    lambda_ : float (default=1.)
        Trade-off parameter
    
    gamma : float (default=4.)
        Margin parameter.

    Attributes
    ----------
    encoder_ : tensorflow Model
        encoder network.
        
    task_ : tensorflow Model
        Principal task network.
        
    discriminator_ : tensorflow Model
        Adversarial task network.
        
    history_ : dict
        history of the losses and metrics across the epochs.
        If ``yt`` is given in ``fit`` method, target metrics
        and losses are recorded too.
        
    Examples
    --------
    >>> Xs = np.concatenate((np.random.random((100, 1)),
    ...                      np.zeros((100, 1))), 1)
    >>> Xt = np.concatenate((np.random.random((100, 1)),
    ...                      np.ones((100, 1))), 1)
    >>> ys = 0.2 * Xs[:, 0]
    >>> yt = 0.2 * Xt[:, 0]
    >>> model = MDD(random_state=0)
    >>> model.fit(Xs, ys, Xt, yt, epochs=100, verbose=0)
    >>> model.history_["task_t"][-1]
    0.0009...
        
    References
    ----------
    .. [1] `[1] <https://arxiv.org/pdf/1904.05801.pdf>`_ Y. Zhang, \
T. Liu, M. Long, and M. Jordan. "Bridging theory and algorithm for \
domain adaptation". ICML, 2019.
    """
    def __init__(self, 
                 encoder=None,
                 task=None,
                 Xt=None,
                 yt=None,
                 lambda_=1.,
                 gamma=4.,
                 copy=True,
                 verbose=1,
                 random_state=None,
                 **params):
            
        names = self._get_param_names()
        kwargs = {k: v for k, v in locals().items() if k in names}
        kwargs.update(params)
        super().__init__(**kwargs)   
    
        
    def train_step(self, data):
        # Unpack the data.
        Xs, Xt, ys, yt = self._unpack_data(data)
        
        # Single source
        Xs = Xs[0]
        ys = ys[0]
        
        # If crossentropy take argmax of preds
        if hasattr(self.task_loss_, "name"):
            name = self.task_loss_.name
        elif hasattr(self.task_loss_, "__name__"):
            name = self.task_loss_.__name__
        else:
            name = self.task_loss_.__class__.__name__
       
        # loss
        with tf.GradientTape() as task_tape, tf.GradientTape() as enc_tape, tf.GradientTape() as disc_tape:
            
            # Forward pass
            Xs_enc = self.encoder_(Xs, training=True)
            ys_pred = self.task_(Xs_enc, training=True)
            ys_disc = self.discriminator_(Xs_enc, training=True)
            
            Xt_enc = self.encoder_(Xt, training=True)
            yt_pred = self.task_(Xt_enc, training=True)
            yt_disc = self.discriminator_(Xt_enc, training=True)
            
            # Reshape
            ys_pred = tf.reshape(ys_pred, tf.shape(ys))
            yt_pred = tf.reshape(yt_pred, tf.shape(ys))
            ys_disc = tf.reshape(ys_disc, tf.shape(ys))
            yt_disc = tf.reshape(yt_disc, tf.shape(ys))
            
            # Compute Disc
            if name == "categorical_crossentropy":
                print("ok")
                argmax_src = tf.one_hot(tf.math.argmax(ys_pred, -1),
                             tf.shape(ys_pred)[1])
                argmax_tgt = tf.one_hot(tf.math.argmax(yt_pred, -1),
                             tf.shape(yt_pred)[1])
                disc_loss_src = self.task_loss_(argmax_src, ys_disc)
                disc_loss_tgt = self.task_loss_(argmax_tgt, yt_disc)
            else:
                disc_loss_src = self.task_loss_(ys_pred, ys_disc)
                disc_loss_tgt = self.task_loss_(yt_pred, yt_disc)
            
            disc_loss_src = tf.reduce_mean(disc_loss_src)
            disc_loss_tgt = tf.reduce_mean(disc_loss_tgt)
            
            # Compute the loss value
            task_loss = self.task_loss_(ys, ys_pred)
            
            disc_loss = self.gamma * disc_loss_src - disc_loss_tgt
            
            task_loss = tf.reduce_mean(task_loss)
            
            enc_loss = task_loss - self.lambda_ * disc_loss
            
            task_loss += sum(self.task_.losses)
            disc_loss += sum(self.discriminator_.losses)
            enc_loss += sum(self.encoder_.losses)
            
        print(task_loss.shape, enc_loss.shape, disc_loss.shape)
            
        # Compute gradients
        trainable_vars_task = self.task_.trainable_variables
        trainable_vars_enc = self.encoder_.trainable_variables
        trainable_vars_disc = self.discriminator_.trainable_variables
        
        gradients_task = task_tape.gradient(task_loss, trainable_vars_task)
        gradients_enc = enc_tape.gradient(enc_loss, trainable_vars_enc)
        gradients_disc = disc_tape.gradient(disc_loss, trainable_vars_disc)
        
        # Update weights
        self.optimizer.apply_gradients(zip(gradients_task, trainable_vars_task))
        self.optimizer.apply_gradients(zip(gradients_enc, trainable_vars_enc))
        self.optimizer.apply_gradients(zip(gradients_disc, trainable_vars_disc))
        
        # Update metrics
        self.compiled_metrics.update_state(ys, ys_pred)
        self.compiled_loss(ys, ys_pred)
        # Return a dict mapping metric names to current value
        logs = {m.name: m.result() for m in self.metrics}
        # disc_metrics = self._get_disc_metrics(ys_disc, yt_disc)
        logs.update({"disc_loss": disc_loss})
        return logs
    
    
    def _initialize_networks(self):
        if self.encoder is None:
            self.encoder_ = get_default_encoder(name="encoder")
        else:
            self.encoder_ = check_network(self.encoder,
                                          copy=self.copy,
                                          name="encoder")
        if self.task is None:
            self.task_ = get_default_task(name="task")
        else:
            self.task_ = check_network(self.task,
                                       copy=self.copy,
                                       name="task")
        if self.task is None:
            self.discriminator_ = get_default_task(name="discriminator")
        else:
            self.discriminator_ = check_network(self.task,
                                                copy=self.copy,
                                                name="discriminator")
