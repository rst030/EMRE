'''fitting module. it has functions for fitting the tune picture. Values extracted are Q. Values passed are
tunepicture array, array of (calibrated) frequencies, central frequency.'''
'''method 1: cutting out the dip. we will need to plot it always, but we can use the original window's plotter for that.'''
import numpy as np
from scipy.signal import savgol_filter #great invention
from scipy.optimize import curve_fit

sweep_scale_factor = 6.94e4  # MHz/tunepicture_unit_interval

def cut_dip(scale_corrected_frequencies,tunepicture):
    '''first, correct for the baseline. Get the baseline from the very left points of the tunepicture'''
    data_for_baseline_correction = tunepicture[0:100]
    coordinates_for_baseline_correction = scale_corrected_frequencies[0:100]
    baseline = np.polyfit(coordinates_for_baseline_correction,data_for_baseline_correction,0) #fit with a horizontal line

    '''correcting tune picture for baseline:'''
    new_tunepicture = (np.array(tunepicture) - baseline)/max(np.array(tunepicture - baseline))
    #tunepicture = new_tunepicture.tolist()
    '''rescaling the time scale to frequencies:'''
    '''we do analysis in arrays and we do data manipulation in lists. It is just more convenient.'''
    '''looking for maximal elements. lets do smothing here first:'''
    smooth_tunepicture = savgol_filter(new_tunepicture, 27,2) #sav-gol(data,window,order)
    smooth_tunepicture = smooth_tunepicture.tolist()

    '''after smothing, we are looking for minima. Let's cut out the zeros:'''
    treshold = 1/45 #a treshold where we say there is no noise but rather tunepicture
    counter=0
    for k in smooth_tunepicture:
        counter+=1
        if (abs(k) > treshold):
            break
    cut_index_from_the_left = counter
    '''here we figured out the left limit of the tunepicture. Let's shorten it:'''
    tunepicture = smooth_tunepicture[counter+25:] #+25 because the MW bridge on the Lyra has sharp rise
    scale_corrected_frequencies = scale_corrected_frequencies[counter+25:]
    '''now let's cut the tune picture from the right:'''
    for k in range(1,len(tunepicture)):
        if(abs(tunepicture[-k])>treshold):
            break
    tunepicture = tunepicture[:-k-50]
    scale_corrected_frequencies = scale_corrected_frequencies[:-k-50]
    '''now we need to get the dip and to cut it out'''
    '''dip is where tunepicture starts to decrease. lets differentiate with noise. Derivative over longer distances
    change sign -> extremum +- = max -+ = min (center of the dip)'''

    index = 0
    delta_old = 0

    left_lim = 0  # left limit of the dip
    right_lim = 0  # right limit of the dip
    dip_center = 0  # center of the dip

    while ((index+45)<len(tunepicture)):

        delta_1 = tunepicture[index + 45] - tunepicture[index]

        if delta_1 < 0:
            if delta_old > 0:
                print('local maximum detected at N = %d'%index)
                if left_lim == 0:
                    left_lim = index
                else:
                    if right_lim == 0:
                        right_lim = index
        if delta_1 > 0:
            if delta_old < 0:
                print('dip center detected at N = %d'%index)
                dip_center = index

        delta_old = delta_1
        index += 1

    '''now,when the dip is detected, let's cut it out:'''
    if left_lim < right_lim: #if detected correctly, this should hold.
        tunepicture_cut = tunepicture[:left_lim - 10] + tunepicture[right_lim + 10:]
        scale_corrected_frequencies_cut = scale_corrected_frequencies[:left_lim - 10] + scale_corrected_frequencies[right_lim + 10:]

        left_lim_of_the_raw_tp = left_lim + cut_index_from_the_left
        right_lim_of_the_raw_tp = right_lim + cut_index_from_the_left
        dip_center_of_the_raw_tp = dip_center + cut_index_from_the_left


    return scale_corrected_frequencies_cut, tunepicture_cut, left_lim_of_the_raw_tp, right_lim_of_the_raw_tp, dip_center_of_the_raw_tp


def correct_for_background(raw_frequencies, raw_tunepicture):

    ''' main method to be called.
    fit the background with a polynomial of degree 3.
    input: vector of 'raw' frequencies aka time vector from the scope and a raw tunepicture
    output: scaled frequency vector, bg-corrected tunepicture'''

    scale_corrected_frequencies = np.array(raw_frequencies)*sweep_scale_factor # frequencies are in in MHz. The conversion factor is: 6.94e4 MHz/pt.
    scale_corrected_frequencies = scale_corrected_frequencies.tolist()

    cut_frequencies,cut_tunepicture, left_index, right_index, center_index = cut_dip(scale_corrected_frequencies, raw_tunepicture) #detected the dip, cut the dip!
    bg_fit_coefs = np.polyfit(cut_frequencies,cut_tunepicture,4) #fit the bg only, without the dip. Got the fit coefficients.

    bg_coords, bg_parabola = get_background(scale_corrected_frequencies, bg_fit_coefs)  #create background vector from the fit coefficients and a frequency vector
    print('len of raw t/p: %d'%len(raw_tunepicture))
    bg_corrected_tunepicture = np.array(raw_tunepicture) - bg_parabola #subtracting the bg
    '''heres our dip:'''
    dip_coords = scale_corrected_frequencies[left_index-25:right_index+25]
    bg_corrected_dip = bg_corrected_tunepicture[left_index-25:right_index+25]

    '''finally, lets correct for the background and scale the dip'''
    shift_value = bg_corrected_dip[1] #lets simply shift the dip to its left-most value.
    bg_corrected_dip = bg_corrected_dip - shift_value
    scaled_dip = bg_corrected_dip/abs(min(bg_corrected_dip))
    #return scale_corrected_frequencies, bg_corrected_tunepicture
    return(dip_coords,scaled_dip)

def get_derivative(x,y):
    smooth_y = savgol_filter(y, 37, 3)  # sav-gol(data,window,order)
    return x[1:], savgol_filter(np.diff(smooth_y),37,3)

def cut_dip_only(x,y):
    '''detect dip in y, and cut it out. Differentiate the tunepicture:'''
    x_deriv, deriv = get_derivative(x,y)
    # Get the indices of maximum element in the derivative
    spikeindex = np.argmax(deriv)
    deriv = deriv[spikeindex+50:]
    x_deriv = x_deriv[spikeindex+50:]

    x_return = x[spikeindex + 50:]
    y_return = y[spikeindex + 50:]

    '''now we have the derivative that has a min and a max. Between them is our dip. We need to cut it first out.'''
    min_left = np.argmin(deriv)
    max_right = np.argmax(deriv)

    '''cutting the max of the dip from the derivative and making two regions. Where cross 0, there dip starts:'''

    left_part = deriv[0:min_left]
    right_part = deriv[max_right:]

    dip_left_index = np.argmin(np.abs(left_part))
    dip_right_index = np.argmin(np.abs(right_part))-max_right

    x = x_return[0:dip_left_index].tolist() + x_return[dip_right_index:len(x_return)-450].tolist()
    y = y_return[0:dip_left_index].tolist() + y_return[dip_right_index:len(y_return)-450].tolist()


    return x, y, dip_left_index+spikeindex + 50, dip_right_index + spikeindex + 50 # here we return the tunepicture without the dip and the indices of the start and end of the dip.


def get_parabola(raw_time_vector, raw_tune_picture):
    tunepicturearray = np.array(raw_tune_picture)
    timevectorarray= np.array(raw_time_vector)
    '''first detect and cut out the dip'''
    cut_x, cut_y, left_dip_index, right_dip_index = cut_dip_only(timevectorarray,tunepicturearray)
    '''then fit the picture without dip with a 4-deg pol'''
    fit_coefs = np.polyfit(cut_x, cut_y, 4)  # fit the bg only, without the dip. Got the fit coefficients.
    x = raw_time_vector
    '''build the parabola with the coefficients'''
    parabola =x**4*fit_coefs[0] + x**3*fit_coefs[1] + x**2*fit_coefs[2] + x*fit_coefs[3] + fit_coefs[4]

    return x, parabola, left_dip_index, right_dip_index

def cut(x,y, left, right):
    return x[left:right],y[left:right]

def get_background(frequencies, fit_coefs):
    crds = np.array(frequencies)
    parabola = crds**4*fit_coefs[0] + crds**3*fit_coefs[1] + crds**2*fit_coefs[2] + crds*fit_coefs[3] + fit_coefs[4]
    return crds, parabola.tolist()

'''let us define a Gaussian function'''
def _gaussian(x, amp,cen,sigma):
    return amp*(1/(sigma*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen)/sigma)**2)))
'''and the Lorentzian function'''
def _lorentzian(x, amp, cen, wid):
    return amp/np.pi*(wid/((x-cen)**2+wid**2))
    #return(amp*wid**2/((x-cen)**2+wid**2))
'''and the sech function'''
def _sech(x, amp, cen, wid):
    return amp*np.sech(wid*(x-cen))
    #return(amp*wid**2/((x-cen)**2+wid**2))


def fit_dip(time_vector, bg_corrected_dip, F_in_Hz):
    '''we will fit the dip in the time domain and get its FWHM in seconds.'''
    popt_lorentz, pcov_lorentz = curve_fit(_lorentzian, time_vector, bg_corrected_dip, p0=[-0.1, 1.6, 0.1])  # fit with Lorentz
    lorentz_fit = _lorentzian(time_vector, popt_lorentz[0], popt_lorentz[1], popt_lorentz[2])
    FWHM_lorentz = 2 * popt_lorentz[2] *1e6
    print('fit params:')
    print(popt_lorentz)
    print('width of the dip is %.3f Hz' % FWHM_lorentz)
    print('F = %.2f Hz'%F_in_Hz)
    print('FWHM = %.2f Hz' % FWHM_lorentz)

    Q = F_in_Hz/FWHM_lorentz

    return(time_vector,lorentz_fit, Q)


def get_q_value(scale_corrected_frequencies, bg_corrected_tunepicture, MW_frequency, model):
    #todo: fit a lorentzian
#    data = curve_fit()#todo:carefully have a look on this function)
    popt_gauss, pcov_gauss = curve_fit(_gaussian, scale_corrected_frequencies, bg_corrected_tunepicture, p0=[-1, 5, 3]) #fit with Gauss
    popt_lorentz, pcov_lorentz = curve_fit(_lorentzian, scale_corrected_frequencies, bg_corrected_tunepicture, p0=[-1, 8, 3]) #fit with Lorentz

    gauss_fit = _gaussian(scale_corrected_frequencies,popt_gauss[0],popt_gauss[1],popt_gauss[2])
    lorentz_fit = _lorentzian(scale_corrected_frequencies, popt_lorentz[0], popt_lorentz[1], popt_lorentz[2])

    FWHM_gauss   = 2*popt_gauss[2]*np.sqrt(2*np.log(2)) *1e6 #sigma to FWHM, in HZ!
    FWHM_lorentz = 2*popt_lorentz[2] *1e6
    print('width of the dip is %.3f Hz'%FWHM_lorentz)
    print('center of the dip is %.3f Hz' %MW_frequency)

    center_gauss = popt_gauss[1] *1e6 #MHz to Hz
    center_lorentz = popt_lorentz[1] *1e6 #MHz to Hz

    Q_gauss = MW_frequency / FWHM_gauss #both given  in Hz
    Q_lorentz = MW_frequency / FWHM_lorentz #both given in Hz

    if model=='gauss':
        return(scale_corrected_frequencies, gauss_fit, FWHM_gauss, center_gauss, Q_gauss, lorentz_fit, FWHM_lorentz, center_lorentz, Q_lorentz)
    else:
        return scale_corrected_frequencies, lorentz_fit, FWHM_lorentz, Q_lorentz #(X, Y)
  #  return q, left_HM, left_HM+5
