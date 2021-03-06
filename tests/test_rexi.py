from frexi_sphere.rexi_coefficients import REXIParameters, RexiCoefficients, b_coefficients
from cmath import exp, sqrt, pi
import numpy
import pytest
import sys
import traceback

sys.path.append('../frexi_sphere/faf')
from REXI import REXI
sys.path.pop()

params = REXIParameters()
mu = params.mu
L = params.L
a = params.a

def approx_e_ix(x, h, M, use_Gaussian_approx):
    b = b_coefficients(h, M)

    sum = 0
    if use_Gaussian_approx:
        for m in range(-M, M+1):
            sum += b[m+M] * approxGaussian(x+float(m)*h, h)
    else:
        alpha, beta_re, beta_im = RexiCoefficients(h, M)
        for n in range(len(alpha)):
            denom = (1j*x + alpha[n]);
            sum += (beta_re[n] / denom).real + 1j*(beta_im[n] / denom).real

    return sum


def approx_phi_with_gauss(x, h, M, n):
    b = b_coefficients(h, M, n)

    sum = 0
    for m in range(-M, M+1):
        sum += b[m+M] * numpy.exp(-((x+m*h)*(x+m*h))/(4.0*h*h))/sqrt(4.0*pi)

    return sum


def approx_phi(x, alpha, beta):
    sum = 0
    for i in range(len(rexi.alpha)):
        sum += beta[i] / (x + alpha[i])
    return sum


def exact_phi(n, x):
    if n == 0:
        return numpy.exp(1j*x)
    elif n == 1:
        return (numpy.exp(1j*x) - 1.)/(1j*x)
    elif n == 2:
        return -(numpy.exp(1j*x) - 1. -1j*x)/(x**2)
    else:
        print("n must be 1 or 2")

def approxGaussian(x, h):
    """
    evaluate approximation of Gaussian basis function
    with sum of complex rational functions
    """
    x /= h

    sum = 0

    for l in range(0, len(a)):
        j = l-L

        # WORKS with max error 7.15344e-13
        sum += (a[l]/(1j*x + mu + 1j*j)).real

    return sum


def test_exponential_approx():
    h = 0.2
    M = 64
    for x in range(-int(h*M)+1, int(h*M)):
        exact = exp(1j*x)
        approx = approx_e_ix(x, h, M, True)
        assert abs(exact - approx) < 2.e-11


def test_rexi_gaussian_approx():
    h = 0.2
    for x in range(10):
        exact = exp(-(x*x)/(4.0*h*h))/sqrt(4.0*pi)
        approx = approxGaussian(x, h)
        assert abs(exact - approx) < 7.15344e-13


def test_rexi_exponential_approx():
    h = 0.2
    M = 64
    for x in range(-int(h*M)+1, int(h*M)):
        exact = exp(1j*x)
        approx = approx_e_ix(x, h, M, False)
        assert abs(exact - approx) < 2.e-11

#
# Run some approximations based without rational approximation of Gaussian basis function
#
@pytest.mark.parametrize("n", [0, 1, 2])
def test_rexi_phi_approx_gauss(n):
    h = 1.
    M = 200

    print("Test REXI with Gaussian basis function")
    for x in range(-191, 192, 10):
        exact = exact_phi(n, x)
        approx = approx_phi_with_gauss(x, h, M, n)
        print(x, exact, approx, abs(exact - approx))
        assert abs(exact - approx) < 2.e-11




#
# Run full REXI tests
#
# Only supported for phi0 so far
#
@pytest.mark.parametrize("n", [0])
def test_rexi_phi_approx(n):
    h = 0.2
    M = 128

    # Halve number of poles by exploiting symmetries
    for halve in [True, False]:
        # Merge real and imag approximation
        for merge in [True, False]:
            print("halve: "+str(halve))
            print("merge: "+str(merge))

            rexi = REXI(N=M, h=h, reduce_to_half=halve, merge=merge)
            # Coefficients are now available in
            # rexi.alpha
            #   and
            # rexi.beta

            rexi.runTests()
 


if __name__ == "__main__":
    try:
        test_rexi_phi_approx(0)

    except SystemExit as e:
        sys.exit(e)

    except Exception as e:
        print("* ERROR:")
        print(str(e))
        traceback.print_exc()
        sys.exit(1)

