import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord


def ra_dec_dist_to_cartesian(ra, dec, distance):
    c = SkyCoord(ra=ra * u.degree, dec=dec * u.degree, distance=distance * u.kpc)
    x = c.cartesian.x
    y = c.cartesian.y
    z = c.cartesian.z
    return pd.Series(x.value), pd.Series(y.value), pd.Series(z.value)


redco = [1.62098281e-82, -5.03110845e-77, 6.66758278e-72, -4.71441850e-67, 1.66429493e-62, -1.50701672e-59,
         -2.42533006e-53, 8.42586475e-49, 7.94816523e-45, -1.68655179e-39, 7.25404556e-35, -1.85559350e-30,
         3.23793430e-26, -4.00670131e-22, 3.53445102e-18, -2.19200432e-14, 9.27939743e-11, -2.56131914e-07,
         4.29917840e-04, -3.88866019e-01, 3.97307766e+02]
greenco = [1.21775217e-82, -3.79265302e-77, 5.04300808e-72, -3.57741292e-67, 1.26763387e-62, -1.28724846e-59,
           -1.84618419e-53, 6.43113038e-49, 6.05135293e-45, -1.28642374e-39, 5.52273817e-35, -1.40682723e-30,
           2.43659251e-26, -2.97762151e-22, 2.57295370e-18, -1.54137817e-14, 6.14141996e-11, -1.50922703e-07,
           1.90667190e-04, -1.23973583e-02, -1.33464366e+01]
blueco = [2.17374683e-82, -6.82574350e-77, 9.17262316e-72, -6.60390151e-67, 2.40324203e-62, -5.77694976e-59,
          -3.42234361e-53, 1.26662864e-48, 8.75794575e-45, -2.45089758e-39, 1.10698770e-34, -2.95752654e-30,
          5.41656027e-26, -7.10396545e-22, 6.74083578e-18, -4.59335728e-14, 2.20051751e-10, -7.14068799e-07,
          1.46622559e-03, -1.60740964e+00, 6.85200095e+02]

redco = np.poly1d(redco)
greenco = np.poly1d(greenco)
blueco = np.poly1d(blueco)


def bv2rgb(b_g_ci):
    # convert to temp K
    temp = 4600 * (1 / (0.92 * b_g_ci + 1.7) + 1 / (0.92 * b_g_ci + 0.62))
    # convert to RGB
    return (
        max(0, min(255, redco(temp))) / 255.,
        max(0, min(255, greenco(temp))) / 255.,
        max(0, min(255, blueco(temp))) / 255.)


def dot_size_from_mag(g_mag, max_mag=19):
    return 2 ** (max_mag - g_mag)
