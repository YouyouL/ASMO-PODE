# evaluate marginal pdf of the results by MCMC and similar algorithms
from __future__ import division
import numpy as np
from scipy import stats
from functools import partial
import matplotlib.pyplot as plt


def my_scott_fac(obj, fac=1.0):
    """ compute band width with Scott's Rule, multiplied by a constant factor
        n: number of points
        d: number of dimensions
        fac: factor
    """
    return np.power(obj.n, -1. / (obj.d + 4)) * fac


def my_silverman_fac(obj, fac=1.0):
    """ compute band width with Silverman's Rule, multiplied by a constant factor
        n: number of points
        d: number of dimensions
        fac: factor
    """
    return np.power((obj.n * (obj.d + 2) / 4.), -1. / (obj.d + 4)) * fac


def est_kpdf(x, xlb, xub, mpdf_true,
             bw_method='scott', fac=1.0, num_ticks=100,
             respath=None, ploteach=False, plotall=False, figname=None,
             label_str='Estimated PDF', paraname=None):
    """ Estiamte kernel PDF of the marginal distributon of x
        x: samples generated by MCMC, or other distribution estimation methods
        xlb: lower bound of x
        xub: upper bound of x
        mpdf_true: true marginal pdf function
        bw_method: band width method, can be 'scott', 'silverman',
                   'scott_fac' (Scott's Rule, multiplied by a constant factor)
                   'silverman_fac' (Silverman's Rule, multiplied by a constant factor)
        fac: factor in 'scott_fac' or 'silverman_fac'
        num_ticks: number of ticks in x-axis
        respath: result path to save figures
        ploteach: plot individual mpdf in each figure
        plotall: plot all mpdf in one figure
        figname: figure file name
        label_str: label string in the legend
        paraname: parameter names
    """
    [n, d] = x.shape

    if respath is None:
        respath = '.'
    if figname is None:
        figname = 'my_mpdf.png'
    if paraname is None:
        paraname = []
        for i in range(d):
            paraname.append('x%d' % (i+1))

    x_ticks = np.zeros([num_ticks, d])
    kpdf_value = np.zeros([num_ticks, d])
    pdf_rmse = np.zeros(d)
    for i in range(d):
        x_ticks[:, i] = np.linspace(xlb[i], xub[i], num_ticks)
        if bw_method == 'scott':
            kde = stats.gaussian_kde(x[:, i], bw_method='scott')
        elif bw_method == 'scott_fac':
            kde = stats.gaussian_kde(x[:, i], bw_method=partial(my_scott_fac, fac=fac))
        elif bw_method == 'silverman':
            kde = stats.gaussian_kde(x[:, i], bw_method='silverman')
        elif bw_method == 'silverman_fac':
            kde = stats.gaussian_kde(x[:, i], bw_method=partial(my_silverman_fac, fac=fac))
        else:
            kde = stats.gaussian_kde(x[:, i], bw_method='scott')
        kpdf_value[:, i] = kde(x_ticks[:, i])
    mpdf_true_value = mpdf_true(x_ticks)

    for i in range(d):
        pdf_rmse[i] = np.sqrt(((kpdf_value[:, i] - mpdf_true_value[:, i]) ** 2).mean())

    if plotall:
        if d <= 3:
            plot_mpdf_each(x, x_ticks, kpdf_value, mpdf_true_value, respath, figname, label_str, paraname)
        else:
            plot_mpdf_all(x, x_ticks, kpdf_value, mpdf_true_value, respath, figname, label_str, paraname)
    if ploteach:
        plot_mpdf_each(x, x_ticks, kpdf_value, mpdf_true_value, respath, figname, label_str, paraname)

    return x_ticks, pdf_rmse, kpdf_value, mpdf_true_value


def plot_mpdf_all(x, x_ticks, kpdf_value, mpdf_true_value, respath, figname, label_str, paraname):
    """ plot marginal pdf in one figure
        x: samples generated by MCMC, or other distribution estimation methods
        x_ticks: evaluated ticks along each dimension
        kpdf_value: kernel pdf estimated by kpdf function
        mpdf_true_value: true marginal pdf values
        respath: result path to save figures
        figname: figure file name
        label_str: label string in the legend
        paraname: parameter names
    """
    [n, d] = x.shape
    ncols = np.int(np.ceil(np.sqrt(d)))
    nrows = np.int(np.ceil(d / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(16, 16))
    #    fig, ax = plt.subplots(nrows, ncols)

    for icol in range(ncols):
        for irow in range(nrows):
            idim = irow * ncols + icol
            if idim < d:
                # ax[irow, icol].plot(x[:,idim], np.zeros(n), 'b+', ms=6)
                ax[irow, icol].plot(x_ticks[:, idim],
                                    kpdf_value[:, idim], 'b-', label=label_str)
                ax[irow, icol].plot(x_ticks[:, idim],
                                    mpdf_true_value[:, idim], 'r--', label="True PDF")
                # ax[irow, icol].legend()
                ax[irow, icol].set_xlabel(paraname[idim])
                ax[irow, icol].set_ylabel('PDF')
            else:
                ax[irow, icol].xaxis.set_visible(False)
                ax[irow, icol].yaxis.set_visible(False)
                ax[irow, icol].set_frame_on(False)
    plt.tight_layout()
    plt.savefig('%s/%s.png' % (respath, figname))
    return 0


def plot_mpdf_each(x, x_ticks, kpdf_value, mpdf_true_value, respath, figname, label_str, paraname):
    """ plot marginal pdf in many figures, each dimension has one figure
        x: samples generated by MCMC, or other distribution estimation methods
        x_ticks: evaluated ticks along each dimension
        kpdf_value: kernel pdf estimated by kpdf function
        mpdf_true_value: true marginal pdf values
        respath: result path to save figures
        figname: figure file name
        label_str: label string in the legend
        paraname: parameter names
    """
    [n, d] = x.shape
    for idim in range(d):
        plt.figure()
        plt.plot(x[:, idim], np.zeros(n), 'b+', ms=6)
        plt.plot(x_ticks[:, idim], kpdf_value[:, idim], 'b-', label=label_str)
        plt.plot(x_ticks[:, idim], mpdf_true_value[:, idim], 'r--', label="True PDF")
        plt.legend()
        plt.xlabel('x%d' % idim)
        plt.ylabel('PDF')
        plt.savefig('%s/%s_%s.png' % (respath, figname, paraname[idim]))
    return 0
