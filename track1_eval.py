#!/usr/local/bin/python

"""N2C2 Track 1 evaluation script."""
from __future__ import division

import argparse
import glob
import os
from collections import defaultdict
from xml.etree import cElementTree


class ClinicalCriteria(object):
    """Criteria in the Track 1 documents."""

    def __init__(self, tid, value):
        """Init."""
        self.tid = tid.strip().upper()
        self.ttype = self.tid
        self.value = value.lower().strip()

    def equals(self, other, mode='strict'):
        """Return whether the current criteria is equal to the one provided."""
        if other.tid == self.tid and other.value == self.value:
            return True
        return False


class RecordTrack1(object):
    """Record for Track 2 class."""

    def __init__(self, file_path):
        self.path = os.path.abspath(file_path)
        self.basename = os.path.basename(self.path)
        self.annotations = self._get_annotations()
        self.text = None

    @property
    def tags(self):
        return self.annotations['tags']

    def _get_annotations(self):
        """Return a dictionary with all the annotations in the .ann file."""
        annotations = defaultdict(dict)
        annotation_file = cElementTree.parse(self.path)
        for tag in annotation_file.findall('.//TAGS/*'):
            criterion = ClinicalCriteria(tag.tag.upper(), tag.attrib['met'])
            annotations['tags'][tag.tag.upper()] = criterion
            if tag.attrib['met'] not in ('met', 'not met'):
                assert '{}: Unexpected value ("{}") for the {} tag!'.format(
                    self.path, criterion.value, criterion.ttype)
        return annotations


class Measures(object):
    """Abstract methods and var to evaluate."""

    def __init__(self, tp=0, tn=0, fp=0, fn=0):
        """Initizialize."""
        assert type(tp) == int
        assert type(tn) == int
        assert type(fp) == int
        assert type(fn) == int
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn

    def precision(self):
        """Compute Precision score."""
        try:
            return self.tp / (self.tp + self.fp)
        except ZeroDivisionError:
            return 0.0

    def recall(self):
        """Compute Recall score."""
        try:
            return self.tp / (self.tp + self.fn)
        except ZeroDivisionError:
            return 0.0

    def f_score(self, beta=1):
        """Compute F1-measure score."""
        assert beta > 0.
        try:
            num = (1 + beta**2) * (self.precision() * self.recall())
            den = beta**2 * (self.precision() + self.recall())
            return num / den
        except ZeroDivisionError:
            return 0.0

    def f1(self):
        """Compute the F1-score (beta=1)."""
        return self.f_score(beta=1)

    def specificity(self):
        """Compute Specificity score."""
        try:
            return self.tn / (self.fp + self.tn)
        except ZeroDivisionError:
            return 0.0

    def sensitivity(self):
        """Compute Sensitivity score."""
        return self.recall()

    def auc(self):
        """Compute AUC score."""
        return (self.sensitivity() + self.specificity()) / 2


class SingleEvaluator(object):
    """Evaluate two single files."""

    def __init__(self, doc1, doc2, track, mode='strict', key=None, verbose=False):
        """Initialize."""
        assert isinstance(doc1, RecordTrack1)
        assert isinstance(doc2, RecordTrack1)
        assert mode in ('strict', 'lenient')
        assert doc1.basename == doc2.basename
        self.scores = {'tags': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0},
                       'relations': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}}
        self.doc1 = doc1
        self.doc2 = doc2
        if key:
            gol = [t for t in doc1.tags.values() if t.ttype == key]
            sys = [t for t in doc2.tags.values() if t.ttype == key]
        else:
            gol = [t for t in doc1.tags.values()]
            sys = [t for t in doc2.tags.values()]
        self.scores['tags']['tp'] = len({s.tid for s in sys for g in gol if g.equals(s, mode)})
        self.scores['tags']['fp'] = len({s.tid for s in sys}) - self.scores['tags']['tp']
        self.scores['tags']['fn'] = len({g.tid for g in gol}) - self.scores['tags']['tp']
        self.scores['tags']['tn'] = 0
        if verbose and track == 2:
            tps = {s for s in sys for g in gol if g.equals(s, mode)}
            fps = set(sys) - tps
            fns = set()
            for g in gol:
                if not len([s for s in sys if s.equals(g, mode)]):
                    fns.add(g)
            for e in fps:
                print('FP: ' + str(e))
            for e in fns:
                print('FN:' + str(e))


class MultipleEvaluator(object):
    """Evaluate two sets of files."""

    def __init__(self, corpora, tag_type=None, mode='strict',
                 verbose=False):
        """Initialize."""
        assert isinstance(corpora, Corpora)
        assert mode in ('strict', 'lenient')
        self.scores = None
        if corpora.track == 1:
            self.track1(corpora)
        else:
            self.track2(corpora, tag_type, mode, verbose)

    def track1(self, corpora):
        """Compute measures for Track 1."""
        self.tags = ('ABDOMINAL', 'ADVANCED-CAD', 'ALCOHOL-ABUSE',
                     'ASP-FOR-MI', 'CREATININE', 'DIETSUPP-2MOS',
                     'DRUG-ABUSE', 'ENGLISH', 'HBA1C', 'KETO-1YR',
                     'MAJOR-DIABETES', 'MAKES-DECISIONS', 'MI-6MOS')
        self.scores = defaultdict(dict)
        metrics = ('p', 'r', 'f1', 'specificity', 'auc')
        values = ('met', 'not met')
        self.values = {'met': {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0},
                       'not met': {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}}

        def evaluation(corpora, value, scores):
            predictions = defaultdict(list)
            for g, s in corpora.docs:
                for tag in self.tags:
                    predictions[tag].append(
                        (g.tags[tag].value == value, s.tags[tag].value == value))
            for tag in self.tags:
                # accumulate for micro overall measure
                self.values[value]['tp'] += predictions[tag].count((True, True))
                self.values[value]['fp'] += predictions[tag].count((False, True))
                self.values[value]['tn'] += predictions[tag].count((False, False))
                self.values[value]['fn'] += predictions[tag].count((True, False))

                # compute per-tag measures
                measures = Measures(tp=predictions[tag].count((True, True)),
                                    fp=predictions[tag].count((False, True)),
                                    tn=predictions[tag].count((False, False)),
                                    fn=predictions[tag].count((True, False)))
                scores[(tag, value, 'p')] = measures.precision()
                scores[(tag, value, 'r')] = measures.recall()
                scores[(tag, value, 'f1')] = measures.f1()
                scores[(tag, value, 'specificity')] = measures.specificity()
                scores[(tag, value, 'auc')] = measures.auc()
            return scores

        self.scores = evaluation(corpora, 'met', self.scores)
        self.scores = evaluation(corpora, 'not met', self.scores)

        for measure in metrics:
            for value in values:
                self.scores[('macro', value, measure)] = sum(
                    [self.scores[(t, value, measure)] for t in self.tags]) / len(self.tags)


def evaluate(corpora, mode='strict', verbose=False):
    """Run the evaluation by considering only files in the two folders."""
    assert mode in ('strict', 'lenient')
    evaluator_s = MultipleEvaluator(corpora, verbose)
    if corpora.track == 1:
        macro_f1, macro_auc = 0, 0
        print('{:*^96}'.format(' TRACK 1 '))
        print('{:20}  {:-^30}    {:-^22}    {:-^14}'.format('', ' met ',
                                                            ' not met ',
                                                            ' overall '))
        print('{:20}  {:6}  {:6}  {:6}  {:6}    {:6}  {:6}  {:6}    {:6}  {:6}'.format(
            '', 'Prec.', 'Rec.', 'Speci.', 'F(b=1)', 'Prec.', 'Rec.', 'F(b=1)', 'F(b=1)', 'AUC'))
        for tag in evaluator_s.tags:
            print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}'.format(
                tag.capitalize(),
                evaluator_s.scores[(tag, 'met', 'p')],
                evaluator_s.scores[(tag, 'met', 'r')],
                evaluator_s.scores[(tag, 'met', 'specificity')],
                evaluator_s.scores[(tag, 'met', 'f1')],
                evaluator_s.scores[(tag, 'not met', 'p')],
                evaluator_s.scores[(tag, 'not met', 'r')],
                evaluator_s.scores[(tag, 'not met', 'f1')],
                (evaluator_s.scores[(tag, 'met', 'f1')] + evaluator_s.scores[(tag, 'not met', 'f1')])/2,
                evaluator_s.scores[(tag, 'met', 'auc')]))
            macro_f1 += (evaluator_s.scores[(tag, 'met', 'f1')] + evaluator_s.scores[(tag, 'not met', 'f1')])/2
            macro_auc += evaluator_s.scores[(tag, 'met', 'auc')]
        print('{:20}  {:-^30}    {:-^22}    {:-^14}'.format('', '', '', ''))
        m = Measures(tp=evaluator_s.values['met']['tp'],
                     fp=evaluator_s.values['met']['fp'],
                     fn=evaluator_s.values['met']['fn'],
                     tn=evaluator_s.values['met']['tn'])
        nm = Measures(tp=evaluator_s.values['not met']['tp'],
                      fp=evaluator_s.values['not met']['fp'],
                      fn=evaluator_s.values['not met']['fn'],
                      tn=evaluator_s.values['not met']['tn'])
        print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}'.format(
            'Overall (micro)', m.precision(), m.recall(), m.specificity(),
            m.f1(), nm.precision(), nm.recall(), nm.f1(),
            (m.f1() + nm.f1()) / 2, m.auc()))
        print('{:>20}  {:<5.4f}  {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}  {:<5.4f}    {:<5.4f}  {:<5.4f}'.format(
            'Overall (macro)',
            evaluator_s.scores[('macro', 'met', 'p')],
            evaluator_s.scores[('macro', 'met', 'r')],
            evaluator_s.scores[('macro', 'met', 'specificity')],
            evaluator_s.scores[('macro', 'met', 'f1')],
            evaluator_s.scores[('macro', 'not met', 'p')],
            evaluator_s.scores[('macro', 'not met', 'r')],
            evaluator_s.scores[('macro', 'not met', 'f1')],
            macro_f1 / len(evaluator_s.tags),
            evaluator_s.scores[('macro', 'met', 'auc')]))
        print()
        print('{:>20}  {:^74}'.format('', '  {} files found  '.format(len(corpora.docs))))


class Corpora(object):

    def __init__(self, folder1, folder2, track_num):
        """Initialize."""
        extensions = {1: '*.xml', 2: '*.ann'}
        file_ext = extensions[track_num]
        self.track = track_num
        self.folder1 = folder1
        self.folder2 = folder2
        files1 = set([os.path.basename(f) for f in glob.glob(
            os.path.join(folder1, file_ext))])
        files2 = set([os.path.basename(f) for f in glob.glob(
            os.path.join(folder2, file_ext))])
        common_files = files1 & files2     # intersection
        if not common_files:
            print('ERROR: None of the files match.')
        else:
            if files1 - common_files:
                print('Files skipped in {}:'.format(self.folder1))
                print(', '.join(sorted(list(files1 - common_files))))
            if files2 - common_files:
                print('Files skipped in {}:'.format(self.folder2))
                print(', '.join(sorted(list(files2 - common_files))))
        self.docs = []
        for file in common_files:
            if track_num == 1:
                g = RecordTrack1(os.path.join(self.folder1, file))
                s = RecordTrack1(os.path.join(self.folder2, file))
            self.docs.append((g, s))


def main(f1, f2, track, verbose=False):
    """Main."""
    corpora = Corpora(f1, f2, track)
    if corpora.docs:
        evaluate(corpora, verbose=verbose)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='n2c2: Track 1 evaluation script')
    parser.add_argument('folder1', help='First data folder path (gold)')
    parser.add_argument('folder2', help='Second data folder path (system)')
    args = parser.parse_args()
    main(os.path.abspath(args.folder1), os.path.abspath(args.folder2), 1)
