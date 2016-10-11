# -*- coding: utf-8 -*-
_JAVA_PKG = "com.genestack.api.files."

AUXILIARY_FILE = _JAVA_PKG + "IAuxilaryFile"
FOLDER = _JAVA_PKG + "IFolder"
SEARCH_FOLDER = _JAVA_PKG + "ISearchFolder"
INDEX_FILE = _JAVA_PKG + "IIndexFile"

APPLICATION_PAGE_FILE = _JAVA_PKG + "IApplicationPageFile"
DICTIONARY_FILE = _JAVA_PKG + "IDictionaryFile"
PREFERENCES_FILE = _JAVA_PKG + "IPreferencesFile"
RAW_FILE = _JAVA_PKG + "IRawFile"
REPORT_FILE = _JAVA_PKG + "IReportFile"

_JAVA_BIO_PKG = "com.genestack.bio.files."

EXPERIMENT = _JAVA_BIO_PKG + "IExperiment"
REFERENCE_GENOME = _JAVA_BIO_PKG + "IReferenceGenome"
VARIATION_FILE = _JAVA_BIO_PKG + "IVariationFile"
CODON_TABLE = _JAVA_BIO_PKG + "ICodonTable"
HT_SEQ_COUNTS = _JAVA_BIO_PKG + "IHTSeqCounts"
UNALIGNED_READS = _JAVA_BIO_PKG + "IUnalignedReads"
ALIGNED_READS = _JAVA_BIO_PKG + "IAlignedReads"

ASSAY = _JAVA_BIO_PKG + "IAssay"
SEQUENCING_ASSAY = _JAVA_BIO_PKG + "ISequencingAssay"
MICROARRAY_ASSAY = _JAVA_BIO_PKG + "IMicroarrayAssay"

DIFFERENTIAL_EXPRESSION_FILE = _JAVA_BIO_PKG + "IDifferentialExpressionFile"

GENOME_BED_DATA = _JAVA_BIO_PKG + "IGenomeBEDData"
GENOME_WIGGLE_DATA = _JAVA_BIO_PKG + "IGenomeWiggleData"


def is_file_type(type_str):
    types = {v for k, v in globals().iteritems() if (not k.startswith("_") and isinstance(v, basestring))}
    return type_str in types
