import sys
import imageio

def saturation(im):
    x, y = im.shape
    return im.sum() / (x * y * 255)


def evaluate(file):
    return saturation(imageio.imread(file)) >= 0.99


if __name__ == '__main__':
    for f in sys.argv[1:]:
        its_blank = 'yes' if evaluate(f) else 'no'
        print(f, its_blank)
