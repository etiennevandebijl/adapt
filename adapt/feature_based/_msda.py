"""
Marginalized Stacked Denoising Autoencoder
"""



class mSDA:
    """
    mSDA: marginalized Stacked Denoising Autoencoder.
    
    mSDA is a feature-based domain adaptation method.
    
    The method use denoising **autoencoders** to learn a new robust
    representation of input data.
    
    mSDA first trains an **autoencoder** (composed of an **encoder**
    and a **decoder** networks) to reconstruct a noisy dataset made
    of target and source input data.
    
    The method is based on the assumption that the fitted **encoder**
    will then provide more robust features to domain shifts.
    
    In a second time, an **estimator** is trained on the encoded feature
    space using labeled source data and labeled target data if provided.
    Thus the algorithm can be used in both **unsupervised** and
    **supervised** DA settings.

    Parameters
    ----------
    get_encoder : callable, optional (default=None)
        Constructor for encoder network.
        The constructor should return a tensorflow compiled Model. 
        It should also take at least an ``input_shape`` argument giving
        the input shape of the network.
        If ``None``, a shallow network with 10 neurons is used
        as encoder network.
        
    get_decoder : callable, optional (default=None)
        Constructor for decoder network.
        The constructor should return a tensorflow compiled Model. 
        It should also take at least an ``input_shape`` argument giving
        the input shape of the network and an ``output_shape``
        argument giving the shape of the last layer.
        If ``None``, a shallow network with ``X.shape[1:]`` neurons
        is used.
    
    get_estimator : callable or object, optional (default=None)
        Constructor for the estimator.
        If a callable function is given it should return an estimator
        object (with ``fit`` and ``predict`` methods).
        If a class is given, a new instance of this class will
        be built and used as estimator.
        If get_estimator is ``None``, a ``LinearRegression`` object will be
        used by default as estimator.
        
    noise_lvl: float, optional (default=0.1)
        Standard deviation of gaussian noise added to the input data
        in the denoising autoencoder.
        
    enc_params : dict, optional (default={})
        Additional arguments for ``get_encoder``.
        
    dec_params : dict, optional (default={})
        Additional arguments for ``get_decoder``.
        
    compil_params : key, value arguments, optional
        Additional arguments for autoencoder compiler
        (loss, optimizer...).
        If none, loss is set to ``"mean_squared_error"``
        and optimizer to ``"adam"``.

    Attributes
    ----------
    encoder_ : tensorflow Model
        Fitted encoder network.
        
    decoder_ : tensorflow Model
        Fitted decoder network.
        
    autoencoder_ : tensorflow Model
        Fitted autoencoder network.
        
    estimator_ : object
        Fitted estimator.

    References
    ----------
    .. [1] `[1] <https://arxiv.org/ftp/arxiv/papers/1206/1206.4683.pdf>`_ \
M. Chen, Z. E. Xu, K. Q. Weinberger, and F. Sha. \
"Marginalized denoising autoencoders for domain adaptation". In ICML, 2012.
    """

    def __init__(self, get_encoder=None, get_decoder=None, noise_lvl=0.1,
                 enc_params={}, dec_params={}, **compil_params):
        self.get_encoder = get_encoder
        self.get_decoder = get_decoder
        self.noise_lvl = noise_lvl
        self.enc_params = enc_params
        self.dec_params = dec_params
        self.compil_params = compil_params


    def fit(self, X, y, src_index, tgt_index, tgt_index_labeled=None,
            fit_params_ae=None, **fit_params_tgt):
        """
        Fit mSDA.

        Parameters
        ----------
        X : numpy array
            Input data.

        y : numpy array
            Output data.

        src_index : iterable
            indexes of source labeled data in X, y.

        tgt_index : iterable
            indexes of target unlabeled data in X, y.
            
        tgt_index_labeled : iterable, optional (default=None)
            indexes of target labeled data in X, y.

        fit_params_ae : dict, optional (default=None)
            Arguments given to the fit process of the autoencoder
            (epochs, batch_size...).
            If None, ``fit_params_ae = fit_params``
        
        fit_params : key, value arguments
            Arguments given to the fit method of the estimator
            (epochs, batch_size...).

        Returns
        -------
        self : returns an instance of self
        """
        pass


    def predict(self, X):
        """
        Return the predictions of the estimator on the encoded
        feature space.

        Parameters
        ----------
        X : array
            Input data.

        Returns
        -------
        y_pred : array
            Prediction of ``estimator_``.
        """
        pass

