__version__ = '0.0.1'
__author__ = 'lovit'

try:
    import soynlp
    print('Available soynlp == {}'.format(soynlp.__version__))
except:
    print('First install soynlp using "pip install soynlp" or "git clone https://github.com/lovit/soynlp.git"')
