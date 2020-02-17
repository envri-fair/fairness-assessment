from shortid import ShortId
from rdflib import plugin, ConjunctiveGraph, Graph, URIRef, Literal, BNode
from rdflib.store import Store
from rdflib.namespace import RDF, RDFS, XSD

sid = ShortId()

def _l(g, d, v, n, k, t):
    if isinstance(k, list):
        p = v[k[0]]['uri']
        if k[1] in d:
            if handle_special_cases(g, d[k[1]], v, n, k[0]):
                return
            o = d[k[1]]
        else:
            o = k[1]
    else:
        if handle_special_cases(g, d[k], v, n, k):
            return
        p = v[k]['uri']
        o = d[k]
    
    g.add((n, p, Literal(o, datatype=t)))
    
    
def _b(g, v, n, k, b):
    g.add((n, v[k]['uri'], b))
    
    
def _r(g, d, v, n, k):
    if isinstance(k, list):
        if handle_special_cases(g, d[k[1]], v, n, k[0]):
            return
        p = v[k[0]]['uri']
        o = d[k[1]]
    else:
        if handle_special_cases(g, d[k], v, n, k):
            return
        p = v[k]['uri']
        o = d[k]
    
    if o.find('http') > -1 or o.find('www') > -1 or o.find('@') > -1:
        g.add((n, p, URIRef(o)))
        return
        
    g.add((n, p, URIRef(v[o]['uri'])))
    
    
def _t(g, d, v, n, k):
    if k in d:
        if isinstance(d[k], list):
            for i in d[k]:
                g.add((n, RDF.type, v[i]['uri']))
        else:
            g.add((n, RDF.type, v[d[k]]['uri']))
    else:
        g.add((n, RDF.type, v[k]['uri']))
    
    
def _c(g, d, v, n1, n2, k):
    if (handle_special_cases(g, d, v, n1, k)):
        return
    _b(g, v, n1, k, n2)
    _t(g, d, v, n2, 'Bag')
    for i in d:
        _li(g, v, n2, i)
    
    
def _li(g, v, n, i):
    g.add((n, v['li']['uri'], URIRef(v[i]['uri'])))
    
    
def translate(s, d, v):
    ns = 'http://envri.eu/ns/'
    gid = URIRef('{}G{}'.format(ns, sid.generate()))
    g = Graph(s, gid)
    survey(g, d['survey'], v)
    infrastructure(g, d['infrastructure'], v)
    
    
def survey(g, d, v):
    n = get_uri() # BNode()
    _l(g, d, v, g.identifier, 'date', XSD.date)
    _l(g, d, v, g.identifier, 'version', XSD.string)
    creator(g, d['creator'], v, g.identifier)
    
    
def creator(g, d, v, n):
    n1 = get_uri() # BNode()
    _b(g, v, n, 'creator', n1)
    _l(g, d, v, n1, 'name', XSD.string)
    _r(g, d, v, n1, 'email')
    
    
def infrastructure(g, d, v):
    n = get_uri() # BNode()
    _t(g, d, v, n, 'FAIRAssessment')
    _l(g, d, v, n, ['altLabel', '{} FAIR assessment'.format(d['acronym'])], XSD.string)
    _r(g, d, v, n, ['infrastructure', 'uri'])
    #_l(g, d, v, n, 'acronym', XSD.string)
    #_l(g, d, v, n, ['label', 'name'], XSD.string)
    #_r(g, d, v, n, ['website', 'website'])
    #_c(g, d['domain'], v, n, get_uri(), 'hasDomain')
    _r(g, d, v, n, ['hasDataset', 'URL/IRI of dataset'])
    _r(g, d, v, n, ['hasDiscoveryPortal', 'URL of discovery portal'])
    for r in d['repositories']:
        repository(g, r, v, n, d['acronym'])
        
        
def repository(g, d, v, n, i):
    if (handle_special_cases(g, d, v, n, 'hasRepository')):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'hasRepository', n1)
    _t(g, d, v, n1, 'Repository')
    _r(g, d, v, n1, ['hasRepositoryUrl', 'URL'])
    _l(g, d, v, n1, ['label', 'name'], XSD.string) 
    _l(g, d, v, n1, ['altLabel', '{} repository'.format(i)], XSD.string)
    _t(g, d, v, n1, 'kind')
    _r(g, d, v, n1, ['hasAllocation', 'allocation'])
    _c(g, d['software'], v, n1, get_uri(), 'usesSoftware')
    identifier(g, d['identifier'], v, n1, i, d['name'])
    _c(g, d['certification methods'], v, n1, get_uri(), 'hasCertificationMethods')
    _c(g, d['policies'], v, n1, get_uri(), 'hasPolicies')
    _c(g, d['registries'], v, n1, get_uri(), 'inRegistries')
    _l(g, d, v, n1, ['hasPersistencyGuaranty', 'persistency-guaranty'], XSD.string)
    access(g, d['access mechanisms'], v, n1, i, d['name'])
    data(g, d['data'], v, n1, i, d['name'])
    metadata(g, d['metadata'], v, n1, i, d['name'])
    vocabularies(g, d['vocabularies'], v, n1, i, d['name'])
    datamanagementplans(g, d['data management plans'], v, n, d['name'])
    dataprocessing(g, d['data processing'], v, n1, i, d['name'])
    fairness(g, d['fairness'], v, n1, i, d['name'])
        
        
def identifier(g, d, v, n, i, r):
    if (handle_special_cases(g, d, v, n, 'usesIdentifier')):
        return
    for e in d:
        n1 = get_uri() # BNode()
        _b(g, v, n, 'usesIdentifier', n1)
        _t(g, e, v, n1, 'Identifier')
        _l(g, e, v, n1, ['altLabel', '{} {} identifier'.format(i, r)], XSD.string)
        _t(g, e, v, n1, 'kind')
        _r(g, e, v, n1, ['usesIdentifierSystem', 'system'])
        _l(g, e, v, n1, ['hasLandingPage','landing page'], XSD.bool)
        _l(g, e, v, n1, ['isAssigned', 'assigned'], XSD.string)
        _r(g, e, v, n1, ['usesProvider', 'provider'])
        _c(g, e['includes metadata schema'], v, n1, get_uri(), 'includesMetadataSchema')
        

def access(g, d, v, n, i, r):
    if (handle_special_cases(g, d, v, n, 'hasAccessMechanisms')):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'hasAccessMechanisms', n1)
    _t(g, d, v, n1, 'AccessMechanism')
    _l(g, d, v, n1, ['altLabel', '{} {} access mechanism'.format(i, r)], XSD.string)
    _l(g, d, v, n1, ['hasAuthenticationMethod', 'authentication method'], XSD.string)
    _r(g, d, v, n1, ['hasAccessProtocolUrl', 'access protocol URL'])
    _l(g, d, v, n1, ['accessWithoutCosts', 'access without costs'], XSD.bool)
    _l(g, d, v, n1, ['maintainsOwnUserDatabase', 'own user database maintained'], XSD.bool)
    _r(g, d, v, n1, ['personIdentificationSystem', 'person identification system'])
    _r(g, d, v, n1, ['supportsAccessTechnology', 'major access technology supported'])
    _r(g, d, v, n1, ['usesAuthorisationTechnique', 'authorisation technique'])
    _l(g, d, v, n1, ['contentAccessAuthorizationRequired', 'authorization for accessing content needed'], XSD.bool)
    _c(g, d['data licenses in use'], v, n1, get_uri(), 'usesDataLicenses')
    _r(g, d, v, n1, ['dataLicenseIri', 'data license IRI'])
    _l(g, d, v, n1, ['openAccessMetadata', 'metadata openly available'], XSD.bool)
    
    
def data(g, d, v, n, i, r):
    if (handle_special_cases(g, d, v, n, 'hasData')):
        return
    for e1 in d:
        n1 = get_uri() # BNode()
        _b(g, v, n, 'hasData', n1)
        _t(g, e1, v, n1, 'Data')
        _l(g, e1, v, n1, ['altLabel', '{} {} data'.format(i, r)], XSD.string)
        _t(g, e1, v, n1, 'type name')
        _c(g, e1['registered data schema'], v, n1, get_uri(), 'dataSchemaIsRegistered')        
        _l(g, e1, v, n, ['searchOnData', 'search on data'], XSD.bool)
        for e2 in e1['preferred formats']:
            n2 = get_uri() # BNode()
            _b(g, v, n1, 'hasPreferredFormat', n2)
            _t(g, e2, v, n2, 'PreferredFormat')
            _r(g, e2, v, n2, ['hasFormatName', 'format name'])
            _c(g, e2['metadata types in data headers'], v, n2, get_uri(), 'hasDataHeaderMetadataTypes')
            
    
def metadata(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'hasMetadata'):
        return
    n1 = get_uri()
    _b(g, v, n, 'hasMetadata', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} metadata'.format(i, r)], XSD.string)
    metadata_schema(g, d['schema'], v, n1, i, r)
    _l(g, d, v, n1, ['hasMachineReadableProvenance', 'machine readable provenance'], XSD.bool)
    _l(g, d, v, n1, ['categoriesAreDefinedInRegistries', 'categories defined in registries'], XSD.bool)
    _l(g, d, v, n1, ['persistentIdentifiersAreIncluded', 'PIDs included'], XSD.bool)
    _r(g, d, v, n1, ['hasPrimaryStorageFormat', 'primary storage format'])
    _c(g, d['export formats supported'], v, n1, get_uri(), 'supportedExportFormats')
    _l(g, d, v, n1, ['searchEngineIndexing', 'search engine indexing'], XSD.bool)
    _c(g, d['exchange/harvesting methods'], v, n1, get_uri(), 'hasHarvestingMethods')
    _r(g, d, v, n1, ['hasLocalSearchEngineUrl', 'local search engine URL'])
    _c(g, d['external search engine types supported'], v, n1, get_uri(), 'supportsExternalSearchEngineTypes')
    _l(g, d, v, n1, ['includesAccessPolicyStatements', 'access policy statements included'], XSD.bool)
    _r(g, d, v, n1, ['hasMetadataLongevityPlan', 'metadata longevity plan URL'])
    _l(g, d, v, n1, ['isMachineActionable', 'machine actionable'], XSD.bool)
    _r(g, d, v, n1, ['hasMachineReadableDatasetMetadata', 'IRI of machine readable metadata of dataset'])
    
    
def metadata_schema(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'hasSchema'):
        return
    for e1 in d:
        n1 = get_uri() # BNode()
        _b(g, v, n, 'hasSchema', n1)
        _l(g, e1, v, n1, ['altLabel', '{} {} metadata schema'.format(i, r)], XSD.string)
        _r(g, e1, v, n1, ['hasSchemaUrl', 'URL'])
        _r(g, e1, v, n1, ['hasSchemaName', 'name'])
        _c(g, e1['provenance fields included'], v, n1, get_uri(), 'includesProvenanceFields')

    
def vocabularies(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'hasVocabularies'):
        return
    for e1 in d:
        n1 = get_uri() # BNode()
        _b(g, v, n, 'hasVocabularies', n1)
        _l(g, e1, v, n1, ['altLabel', '{} {} vocabularies'.format(i, r)], XSD.string)
        _r(g, e1, v, n1, ['hasVocabularyIri', 'IRI'])
        _l(g, e1, v, n1, ['hasName', 'name'], XSD.string)
        _t(g, e1, v, n1, 'type')
        _r(g, e1, v, n1, ['hasTopic', 'topic'])
        _r(g, e1, v, n1, ['hasSpecificationLanguage', 'specification language'])
        

def datamanagementplans(g, d, v, n, i):
    if (handle_special_cases(g, d, v, n, 'hasDataManagementPlans')):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'hasDataManagementPlans', n1)
    _l(g, d, v, n1, ['altLabel', '{} data management plans'.format(i)], XSD.string)
    _l(g, d, v, n1, ['usesSpecificDataManagementPlanTools', 'specific DMP tools used'], XSD.bool)
    _l(g, d, v, n1, ['appliedDataPublishingSteps', 'data publishing steps applied'], XSD.string)
    _l(g, d, v, n1, ['hasComplianceValidationService', 'compliance validation service'], XSD.bool)
    

def dataprocessing(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'hasDataProcessing'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'hasDataProcessing', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} data processing'.format(i, r)], XSD.string)
    _c(g, d['special data processing steps applied'], v, n1, get_uri(), 'specialDataProcessingStepsApplied')
    _c(g, d['workflow frameworks applied'], v, n1, get_uri(), 'workflowFrameworksApplied')
    _c(g, d['distributed workflows tools used'], v, n1, get_uri(), 'distributedWorkflowsToolsUsed')
    _c(g, d['other analysis services offered'], v, n1, get_uri(), 'otherAnalysisServicesOffered')
    _c(g, d['data products offered'], v, n1, get_uri(), 'dataProductsOffered')

    
def fairness(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'fairness'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'fairness', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} fairness'.format(i, r)], XSD.string)
    fairness_findability(g, d['data findability'], v, n1, i, r)
    fairness_accessibility(g, d['data accessibility'], v, n1, i, r)
    fairness_interoperability(g, d['data interoperability'], v, n1, i, r)
    fairness_reusability(g, d['data re-usability'], v, n1, i, r)

    
def fairness_findability(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'dataFindability'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'dataFindability', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} faireness findability'.format(i, r)], XSD.string)
    _l(g, d, v, n1, ['dataIsFindable', 'data findable'], XSD.bool)
    _c(g, d['gaps'], v, n1, get_uri(), 'gaps')

    
def fairness_accessibility(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'dataAccessibility'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'dataAccessibility', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} faireness accessibility'.format(i, r)], XSD.string)
    _l(g, d, v, n1, ['dataIsAccessible', 'data accessible'], XSD.bool)
    _c(g, d['gaps'], v, n1, get_uri(), 'gaps')

    
def fairness_interoperability(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'dataInteroperability'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'dataInteroperability', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} faireness interoperability'.format(i, r)], XSD.string)
    _l(g, d, v, n1, ['dataIsInteroperable', 'data interoperable'], XSD.bool)
    _c(g, d['gaps'], v, n1, get_uri(), 'gaps')

    
def fairness_reusability(g, d, v, n, i, r):
    if handle_special_cases(g, d, v, n, 'dataReusability'):
        return
    n1 = get_uri() # BNode()
    _b(g, v, n, 'dataReusability', n1)
    _l(g, d, v, n1, ['altLabel', '{} {} faireness reusability'.format(i, r)], XSD.string)
    _l(g, d, v, n1, ['dataIsReusable', 'data reusable'], XSD.bool)
    _c(g, d['gaps'], v, n1, get_uri(), 'gaps')
    

def handle_special_cases(g, d, v, n, k):
    if d is None:
        g.add((n, v[k]['uri'], v['NULL']['uri']))
        return True
    if d is 'NULL':
        g.add((n, v[k]['uri'], v['NULL']['uri']))
        return True
    if d == 'VOID':
        g.add((n, v[k]['uri'], v['VOID']['uri']))
        return True
    if d == 'none':
        g.add((n, v[k]['uri'], v['none']['uri']))
        return True
    if d == 'planned':
        g.add((n, v[k]['uri'], v['planned']['uri']))
        return True
    return False


def get_uri():
    return URIRef('{}R{}'.format('http://envri.eu/ns/', sid.generate()))