import os
from . import helpers
print(globals())
logger = helpers.logger


class Corpus:
    def __init__(self,
                 file_path = None,
                 file_name = None,
                 output_dir = None,
                 tmp_out = None,
                 cleaned_path = None):
        """
        Set up variables.
        _:param: allow advanced usage to set path vars
        """
        self.file_path = file_path
        self.file_name = file_name
        self.output_dir = output_dir
        self.tmp_out = tmp_out
        self.cleaned_path = cleaned_path


    def set_up(self):
        """
        Set up input file and output path manually
        :return:
        """
        helpers.show_message(msg = 'Select an input file',level='info')
        while True:
            try:
                self.file_path = helpers.select_file()
                if not self.file_path: # handle cancel button
                    logger.warning('User cancel, program killed.')
                    exit(0)
                # make sure the input file is valid
                assert os.path.exists(self.file_path) and self.file_path.endswith('.txt')
                break
            except AssertionError:
                helpers.show_message(msg = 'Select a valid input file',level = 'error')
        self.file_name = os.path.basename(self.file_path)[:-4]
        logger.info('Select %s for SVO extraction.', self.file_name)
        helpers.show_message(msg = 'Select a output folder',level = 'info')
        while True:
            try:
                self.output_dir = helpers.select_file(_dir= True)
                if not self.output_dir:
                    logger.warning('User cancel, program killed.')
                    exit(0)
                # make sure output path is valid
                assert os.path.isdir(self.output_dir)
                break
            except AssertionError:
                helpers.show_message('Please select a valid folder','error')
        # create a tmp output dir to hold intermediate files
        logger.info('Set %s as the output folder.',self.output_dir)
        self.tmp_out = os.path.join(self.output_dir, 'tmp')
        if not self.tmp_out:
            exit(0)
        os.makedirs(self.tmp_out, exist_ok=True)
        logger.debug('Create intermediate tmp output folder %s.',self.tmp_out)

        helpers.FILE_PATH = self.file_path
        helpers.FILE_NAME = self.file_name
        helpers.OUT_DIR = self.output_dir
        helpers.TMP_OUT_DIR = self.tmp_out

        logger.debug('Corpus module for %s initiated.', self.file_name)

    def clean_up(self):
        """
        Set the cleaned up path.
        """
        # first log variables
        helpers.log_var('FILE_NAME', 'FILE_PATH', 'OUT_DIR', 'TMP_OUT_DIR')
        self.cleaned_path = helpers.clean_up_file(
            file_name = self.file_name,
            file_path = self.file_path,
            tmp_out = self.tmp_out
        )
        helpers.CLEANED_PATH = self.cleaned_path
        helpers.log_var('CLEANED_PATH')
        logger.debug('Corpus %s cleaned up.',self.file_name)

    def __str__(self):
        return 'Corpus '+self.file_name


class Coref:
    def __init__(self,corpus,coref_methods=None):

        """
        Perform different kinds of co-reference, if user want to use self-defined coref methods,
        the method need to take an input corpus object and return an output file
        :param coref_methods: list of names of co-reference methods, predefined is neural-coref
        """
        self.corpus = corpus
        if coref_methods is None:
            coref_methods = [helpers.neural_coref.__name__]
        self.coref_methods = [x for x in coref_methods]
        self.coref_files = {}

        for each in coref_methods:
            coref_file = globals()['helpers'][each](self.corpus)
            self.coref_files[each] = coref_file

        helpers.log_var('corpus','coref_methods','coref_files',local=True)

    def compare(self, coref_method, comparison_method=None):
        """
        Compare original file with corefed file.
        :param coref_method: String the name of the coref method
        :param comparison_method: self-defined comparison methods that take origin_text and
               corefed text as input and return two tuples of the differences that can be used
               to display the highlighting difference, the default method was implemented with difflib
        :return: tuples with highlight info
        """
        origin_text = open(self.corpus.cleaned_path).read()
        corefed_text = open(self.coref_files[coref_method]).read()
        logger.info('Comparing result from %s co-reference method',coref_method)
        if comparison_method is not None:
            logger.info('Use default comparison method %s',comparison_method)
            return comparison_method(origin_text,corefed_text)
        return helpers.compare_results(origin_text,corefed_text)

    def display(self,coref_method):
        """
        Display with GUI of the difference, editing enabled
        :param coref_method: String the name of the co-reference method
        :return: the edited result
        """
        gui = helpers.GUI(title=('Comparing result from %s',coref_method))
        logger.info('Displaying result from %s, editing enabled',coref_method)
        origin_display,coref_display = self.compare(coref_method)
        gui.create_comparison(ta=origin_display,tb=coref_display)
        result = []
        gui.create_button(gui,text='Finish',callback=helpers.finish_comparison,result=result)
        return result

    def __str__(self):
        return '/n'.join([str(x) for x in self.coref_files])


class NER:
    def __init__(self,corpus = None):
        self.corpus = corpus
        logger.info(str(self.corpus),'selected for NER tagging')
