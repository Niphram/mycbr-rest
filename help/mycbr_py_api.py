import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import requests
import json

from typing import Any
from typing import List
from typing import Tuple
from typing import Dict


# from typing import Mapping
# from typing import NoReturn


class _Constant:
    BASE_URL = 'http://localhost:8080'
    CASE_ID = 'caseID'
    SIMILARITY = 'similarity'


class MyCBRRestApi:
    __base_url = None
    __conceptID = None
    __casebaseID = None
    __amalgamationFunctionID = None
    __columnNames = None

    def __init__(self, base_url=None):

        if base_url is None:
            base_url = _Constant.BASE_URL

        self.__base_url = base_url
        self.__conceptID = self.getAllConcepts()[0]

        self._setColumnNamesForConcept(self.__conceptID)

    def _getCurrentBaseURL(self):
        return self.__base_url

    def _getCurrentConceptID(self):
        return self.__conceptID

    def _getCurrentCasebaseID(self):
        return self.__casebaseID

    def _getCurrentAmalgamationFunctionID(self):
        return self.__amalgamationFunctionID

    def _getCurrentColumnNames(self) -> List[str]:
        """     
        Get the column names that is set in the current instance.

        Returns
        -------
            List[str] : column names, including 'caseID' and 'similarity'.
        """
        return self.__columnNames

    def _setCurrentConceptID(self, conceptID: str = None) -> bool:
        """     
        To set the default concept name.
        Parameters
        ----------
            conceptID : Name of the concept (default: None)
        Returns
        -------
            Boolean : True is concept name is set, else false.
        """

        flag = False

        if (conceptID is not None) and (conceptID is not ''):
            self.__conceptID = conceptID
            if conceptID is self.__conceptID:
                flag = True

        return flag

    def _setCurrentCasebaseID(self, casebaseID: str = None) -> bool:
        """     
        To set the default casebase name.
        Parameters
        ----------
            casebaseID : Name of the casebase (default: None)
        Returns
        -------
            Boolean : True is casebase name is set, else false.
        """

        flag = False

        if (casebaseID is not None) and (casebaseID is not ''):
            self.__casebaseID = casebaseID
            if casebaseID is self.__casebaseID:
                flag = True

        return flag

    def _setCurrentAmalgamationFunctionID(self, amalgamationFunctionID: str = None) -> bool:
        """     
        To set the default amalgamation function.

        Parameters
        ----------
            amalgamationFunctionID : Name of the amalgamation function (default: None)

        Returns
        -------
            Boolean : True is amalgamation function is set, else flase.
        """
        flag = False

        if (amalgamationFunctionID is not None) and (amalgamationFunctionID is not ''):
            self.__amalgamationFunctionID = amalgamationFunctionID
            if amalgamationFunctionID is self.__amalgamationFunctionID:
                flag = True

        return flag

    def _setColumnNamesForConcept(self, conceptID: str = None) -> bool:
        """     
        Set all the possible column names for the given conceptID.

        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            Boolean : True is amalgamation function is set, else flase.
        """

        flag = False

        self.__columnNames = self.getColumnNames(conceptID)

        if self.__columnNames is not None:
            flag = True

        return flag

    def getColumnNames(self, conceptID: str = None) -> List[str]:

        """     
        Get all the possible column names for the given conceptID.

        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            List[str] : column names, including 'caseID' and 'similarity'.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        default_columns = [_Constant.CASE_ID, _Constant.SIMILARITY]
        attributes = list(self.getAllAttributes(conceptID=conceptID).keys())
        # attributes = pd.DataFrame( self.getAllAttributes( conceptID=conceptID)).index.values.tolist()
        column_list = default_columns + attributes

        return column_list

    def __rest_response_to_dataframe(self, response: requests.Response) -> pd.DataFrame:
        """     
        Helper function: convert the request response to pandas DataFrame.

        Parameters
        ----------
            response : response from a REST API call

        Returns
        -------
            DataFrame : To be done.
        """

        response_json = response.json()

        # The below try:, except:, and else: are used to determine if a programme variable is defined or not!
        try:
            self.__columnNames

        except NameError:
            # print('column_list is not defined!!!')
            df = pd.DataFrame(response_json)

        else:

            df = pd.DataFrame(response_json, columns=self.__columnNames)

        df.replace('_unknown_', np.nan, inplace=True)
        # print(df_response_gai)

        if df.empty:
            print("The response from myCBR is empty! Kindly have a look!")
            print("The Dataframe is : ", df)

        return df

    def show_ordered_ssm(
            self,
            df: pd.DataFrame,
            name: str = 'NotProvided',
            ticks_interval: int = 10,
            figsize: Tuple[int, int] = (10, 9),
            isAnnot: bool = False,
            ftm='.2g'
    ) -> pd.DataFrame:

        """

        Get the Self-Similarity Matrix in an ordered form, where the first column has the highest sum.

        Parameters
        ----------
            df : The Self-Similarity Matrix in pandas DataFrame format, where indexs and columns are same i.e. caseIDs.
            name : The name to be shown on the plot title. (default: NotProvided).
            ticks_interval : The interval of ticks for the Self-Similarity heatmap.
            figsize : Figure size of the Heatmap plot (default: (10,10)).
            isAnnot : True, will annotate each cell with its similarity value (default: False).
            ftm :

        Returns
        -------
            DataFrame : Ordered Self-Similarity matrix, NaN represents a caseID was not compared for the similarity.
        """

        ordered_series = df.sum(axis=1).sort_values(ascending=False)
        lis = ordered_series.index.tolist()

        df_1 = df[lis]
        df_temp = df_1.reindex(lis)

        plt.figure(figsize=figsize)

        ax = sns.heatmap(
            df_temp,
            cmap='viridis',
            xticklabels=ticks_interval,
            yticklabels=ticks_interval,
            fmt=ftm,
            annot=isAnnot,
            annot_kws={'size': 9}
        )

        ax.invert_xaxis()

        plt.yticks(rotation=0)
        plt.title('Self-Similarity Matrix (ordered) for : ' + name)

        return df_temp

    # ****************** myCBR-rest API Calls **************************

    def getAllConcepts(self) -> List[str]:
        """ 
        Get all the concepts for the given myCBR project.

            * Sample URL: ~/concepts

        Parameters
        ----------

        Returns
        -------
            List : list of concept IDs.
        """

        final_url = self.__base_url + '/concepts'
        # print(final_url)

        response = requests.get(url=final_url)

        concept_list = response.json()

        return concept_list

    def getCaseBaseIDs(self) -> List[str]:

        """     
        Get all the casebases.

            * Sample URL: ~/casebases

        Parameters
        ----------

        Returns
        -------
            List : list of casebase IDs.
        """

        final_url = self.__base_url + '/casebases'
        # print(final_url)

        response = requests.get(url=final_url)
        casebases = response.json()

        return casebases

    def getAllAmalgamationFunctions(self, conceptID: str = None) -> List[str]:

        """     
        Get all the amalgamation functions for the given conceptID.

            * Sample URL: ~/concepts/patient/amalgamationFunctions 

        Parameters
        ----------
            conceptID : Name of the concept (default: 'self.__conceptID')

        Returns
        -------
            List : list of amalgamation function IDs.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url + '/concepts/' + conceptID + '/amalgamationFunctions'
        # print(final_url)

        response = requests.get(url=final_url)
        # print(response.text)

        amalgamation_list = response.json()

        return amalgamation_list

    def getAllAttributes(self, conceptID: str = None) -> Dict[str, str]:

        """     
        Get all the attributes for the given conceptID.

            * Sample URL: ~/concepts/patient/attributes

        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            Dict[str1, str2] : 
                str1: The attribute name.
                str2: The attribute datatype.
        """
        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url + '/concepts/' + conceptID + '/attributes'
        # print(final_url)

        response = requests.get(url=final_url)
        # print(response.text)

        attribute_list = response.json()

        return attribute_list

    def getActiveAttributes(self, amalgamationFunctionID: str, conceptID: str = None) -> pd.DataFrame:

        """     
        Get all the active attributes for the given conceptID and amalgamation function.

            * Sample URL: ~/concepts/car/amalgamationFunctions/weighted_gsf/getActiveAttributes


        Parameters
        ----------
            amalgamationFunctionID: 
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            pd.DataFrame : where rows are the attributeIDs and column is global similarity function weight.
            The weight = 0 indicates, the respective attribute is not active in the similarity function,
            which means that attribute does not take part in similarity computation.
        """
        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/getActiveAttributes'
        # print(final_url)

        response = requests.get(url=final_url)
        # print(response.text)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = 'attributeID'
        df.columns = ['weight']

        return df

    def getAttributeByID(self, attributeID: str, conceptID: str = None) -> json:

        """     
        Get an attribute by its attributeID for a given conceptID.

            * Sample URL: ~/concepts/patient/attributes/body_main

        Parameters
        ----------
            attributeID : Name of the attribute (default: None)
            conceptID : Name of the concept (default: self.__conceptID)
            
        Returns
        -------
            attribute : json representation of the attribute content.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url + '/concepts/' + conceptID + '/attributes/' + attributeID
        # print(final_url)

        response = requests.get(url=final_url)
        attributes = response.json()

        return attributes

    def getAllAttributeSimilarityFunctions(self, attributeID: str, conceptID: str = None) -> json:

        """     
        Get an attribute similarityFunctions by its attributeID for a given conceptID.

            * Sample URL: ~/concepts/patient/attributes/body_main/similarityFunctions

        Parameters
        ----------
            attributeID : Name of the attribute
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            similarityFunctions : json representation of the attribute similarityFunctions.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url + '/concepts/' + conceptID + '/attributes/' + attributeID + '/similarityFunctions'
        # print(final_url)

        response = requests.get(url=final_url)
        attributes = response.json()

        return attributes

    def addCaseBaseID(self, casebaseID: str) -> bool:

        """ 
        Add a casebaseID.

            * Sample URL : ~/casebases/test_casebase

        Parameters
        ----------
            casebaseID : Name of the case base

        Returns
        -------
            bool : True (casebaseID added), False (casebaseID not added)
        """

        final_url = self.__base_url + '/casebases/' + casebaseID
        # print(final_url)

        response = requests.put(url=final_url)

        return response.json()

    def deleteCaseBaseID(self, casebaseID: str) -> bool:

        """ 
        Add a casebaseID.

            * Sample URL : ~/casebases/test_casebase

        Parameters
        ----------
            casebaseID : Name of the case base

        Returns
        -------
            bool : True (casebaseID deleted), False (casebaseID not deleted)
        """

        final_url = self.__base_url + '/casebases/' + casebaseID
        # print(final_url)

        response = requests.delete(url=final_url)

        return response.json()

    def getAllCasesFromCaseBase(self, conceptID: str = None, casebaseID: str = None) -> pd.DataFrame:

        """ 
        Get all the cases for a given conceptID and casebaseID.

            Sample URL: ~/concepts/patient/casebases/casebase/cases

        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the case base (default: self.__casebaseID)

        Returns
        -------
            Dataframe: pandas Dataframe, where rows are the cases with unique "caseID" and columns are the concept
            attributes.

        Note
        ----
            NaN : The placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url + '/concepts/' + conceptID + '/casebases/' + casebaseID + '/cases'
        # print(final_url)

        response = requests.get(url=final_url)

        df = self.__rest_response_to_dataframe(response)

        return df

    def getCaseByCaseID(self, caseID: str, conceptID: str = None, casebaseID: str = None) -> pd.DataFrame:

        """ 
        Get the cases for the given conceptID, casebaseID, and caseID.

            * Sample URL: ~/concepts/patient/casebases/casebase/cases/patient0

        Parameters
        ----------
            caseID : Unique ID of the case from the CBR system          
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the case base (default: self.__casebaseID) 

        Returns
        -------
            DataFrame : The row is the case and columns are it's concept attributes.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url + '/concepts/' + conceptID + '/casebases/' + casebaseID + '/cases/' + caseID
        # print(final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(pd.Series(response.json()))

        df = df.transpose()

        return df

    def getAllCases(self, conceptID: str = None) -> pd.DataFrame:

        """ 
        Get the cases for the given conceptID.

            * Sample URL: ~/concepts/patient/cases

        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            DataFrame : The row is the case with unique "caseID" and columns are the concept attributes.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url + '/concepts/' + conceptID + '/cases'
        # print(final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json())

        return df

    def getSimilarCasesFromEphemeralCaseBaseWithContent(
            self,
            caseID: str,
            ephemeralCaseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:
        """ 
        Get the cases for the given conceptID.

            * Sample URL: ~/ephemeral/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_var_no_lca_sim
            /retrievalByCaseIDWithContent?caseID=patient0&k=-1

        Parameters
        ----------
            caseID : Name of the concept
            ephemeralCaseIDs : List of cases' IDs to be included in the ephemeral casebase
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: np.size(ephemeralCaseIDs))
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The row is the case with unique "caseID" and columns are the concept attributes.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID
        if k is None:
            k = np.size(ephemeralCaseIDs)

        final_url = self.__base_url \
                    + '/ephemeral/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByCaseIDWithContent?caseID=' + caseID \
                    + '&k=' + str(k)
        # print( final_url)

        payload = ephemeralCaseIDs
        response = requests.post(url=final_url, json=ephemeralCaseIDs)

        df = self.__rest_response_to_dataframe(response)

        df.similarity = pd.to_numeric(df.similarity, errors='ignore')
        df.similarity = df.similarity.round(decimals=deci_precision)

        df = df.sort_values(by=_Constant.SIMILARITY, ascending=False)

        return df

    def getSimilarCasesFromEphemeralCaseBase(
            self,
            queryIDs: List[str],
            ephemeralCaseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Get the cases for the given conceptID.

            * Sample URL: ~/ephemeral/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /retrievalByCaseIDs?k=-1

            * Body : "{ \"queryCaseIDs\": [ \"patient0\", \"patient3\" ],
            \"ephemeralCaseIDs\": [ \"patient1\", \"patient1\" ]}"

        Parameters
        ----------
            queryIDs : The list of query cases' IDs 
            ephemeralCaseIDs : List of cases' IDs to be included in the ephemeral casebase
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: np.size(casebase_list))
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are the cases from the ephemeral casebase with unique "caseID" and columns are
            the query cases' IDs with similarity values.
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID
        if k is None:
            k = np.size(ephemeralCaseIDs)

        final_url = self.__base_url \
                    + '/ephemeral/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByCaseIDs?k=' + str(k)
        # print( final_url)

        payload = dict()
        payload.update([('queryCaseIDs', queryIDs), ('ephemeralCaseIDs', ephemeralCaseIDs)])

        response = requests.post(url=final_url, json=payload)

        df = pd.DataFrame(response.json()).round(deci_precision)

        return df

    def getEphemeralCaseBaseSelfSimilarity(
            self,
            ephemeralCaseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Get the Self-Similarity Matrix for an ephemeral casebase.

            * Sample URL: ~/ephemeral/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /computeSelfSimilarity?k=-1

            * Body : "[ \"patient0\", \"patient3\"]"

        Parameters
        ----------
            ephemeralCaseIDs : List of cases' IDs to be included in the ephemeral casebase.
            amalgamationFunctionID : Name of the amalgamation function.
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: np.size(casebase_list))
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are the cases from the ephemeral casebase with unique "caseID" and columns are are the
            query cases' IDs. NaN represents that a caseID was not compared for the similarity.
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID
        if k is None:
            k = np.size(ephemeralCaseIDs)

        print(':', conceptID, ':', casebaseID, ':', k, ':')

        final_url = self.__base_url \
                    + '/ephemeral/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeSelfSimilarity?k=' + str(k)

        print(final_url)

        payload = ephemeralCaseIDs
        response = requests.post(url=final_url, json=payload)

        df = pd.DataFrame(response.json()).round(deci_precision)

        return df

    def getCaseBaseSelfSimilarity(
            self,
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = -1,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Get the Self-Similarity Matrix for the given casebase.

            * Sample URL: ~/concepts/patient/casebases/casebase
            /computeSelfSimilarity?amalgamationFunctionID=LCA_variables&k=-1

        Parameters
        ----------
            amalgamationFunctionID : Name of the amalgamation function.
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: -1)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are the cases from the casebase with unique "caseID"
            and columns are the query cases' IDs.

        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/computeSelfSimilarity?amalgamationFunctionID=' + amalgamationFunctionID \
                    + '&k=' + str(k)
        # print( final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df[df.columns.sort_values()]  # To rearrange colomns in the ascening order

        return df

    def getSimilarCasesByAttribute(
            self,
            amalgamationFunctionID: str,
            attributeID: str,
            value: Any,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = -1,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Retrieve similar cases by attributeID.

            * Sample URL: ~/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /retrievalByAttribute?Symbol%20attribute%20name=body_main&k=-1&value=back

        Parameters
        ----------
            
            amalgamationFunctionID : Name of the amalgamation function 
            attributeID : Name of the attribute 
            value : Value of the attribute 
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: -1, where -1 means all)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and column is the similarity value.
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByAttribute?Symbol%20attribute%20name=' + attributeID \
                    + '&k=' + str(k) \
                    + '&value=' + value
        # print( final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df.sort_values(by='similarCases', ascending=False)

        df.index.name = _Constant.CASE_ID
        df.columns = [_Constant.SIMILARITY]

        return df

    def getSimilarCasesByCaseID(
            self,
            caseID: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = -1,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Retrieve similar cases by caseID.

            * Sample URL: ~/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /retrievalByCaseID?caseID=patient0&k=-1

        Parameters
        ----------
            caseID : The caseID of the queried case
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: -1, where -1 means all)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and column is the similarity value.
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByCaseID?caseID=' + caseID \
                    + '&k=' + str(k)
        # print( final_url)

        response = requests.get(url=final_url)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = _Constant.CASE_ID
        df.columns = [_Constant.SIMILARITY]
        df = df.round(deci_precision)
        df = df.sort_values(by=_Constant.SIMILARITY, ascending=False)

        return df

    def getSimilarCasesByMultipleCaseIDs(
            self,
            caseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = -1,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Retrieve similar cases for multiple caseIDs.

            * Sample URL: ~/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /retrievalByMultipleCaseIDs?k=1

        Parameters
        ----------
            caseIDs : The list of caseIDs for retrieval
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: -1, where -1 means all)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are the cases from the casebase with unique caseID, and the column are
            the queried caseIDs with their similarity values.
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByMultipleCaseIDs?k=' + str(k)
        # print( final_url)

        payload = caseIDs

        response = requests.post(url=final_url, json=payload)

        df = pd.DataFrame(response.json()).round(deci_precision)

        return df

    def getSimilarCasesByCaseIDWithContent(
            self,
            caseID: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            k: int = -1,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Retrieve similar cases with content by caseID.

            * Sample URL: ~/concepts/patient/casebases/casebase/amalgamationFunctions/LCA_variables
            /retrievalByCaseIDWithContent?caseID=patient0&k=-1

        Parameters
        ----------
            caseID : The caseID of the queried case
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            k : Name of the retrieved cases (default: -1, where -1 means all)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/retrievalByCaseIDWithContent?caseID=' + caseID \
                    + '&k=' + str(k)
        # print( final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json()).round(deci_precision)

        return df

    def compareTwoCases(
            self,
            caseID1: str,
            caseID2: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Retrieve similar cases with content by caseID.

            * Sample URL: ~/analytics/concepts/animal/amalgamationFunctions/rank_wt_all
            /compareTwoCases?caseID_1=animal0&caseID_2=animal2

        Parameters
        ----------
            caseID1 : The caseID of the first case
            caseID2 : The caseID of the second case
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/compareTwoCases?caseID_1=' + caseID1 \
                    + '&caseID_2=' + caseID2
        print(final_url)

        response = requests.get(url=final_url)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = 'attributeID'
        df.columns = ['similarity']
        df = df.round(deci_precision)

        return df

    def computeLocalSimilarityOfTwoCases(
            self,
            caseID1: str,
            caseID2: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the local similarity (attribute similarities) between two caseIDs.

            * Sample URL: ~/analytics/concepts/animal/amalgamationFunctions/rank_wt_all
            /computeLocalSimilarityOfTwoCases?caseID_1=animal0&caseID_2=animal1
            
        Parameters
        ----------
            caseID1 : The caseID of the first case
            caseID2 : The caseID of the second case
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeLocalSimilarityOfTwoCases?' \
                    + 'caseID_1=' + caseID1 \
                    + '&caseID_2=' + caseID2

        print(final_url)

        response = requests.get(url=final_url)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = 'attributeID'
        df.columns = ['similarity']
        df = df.round(deci_precision)

        return df

    def computeGlobalSimilarityOfTwoCases(
            self,
            caseID1: str,
            caseID2: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the global similarity (attribute similarities with normalized weight) between two caseIDs.

            * Sample URL: ~/analytics/concepts/animal/amalgamationFunctions/rank_wt_all
            /computeGlobalSimilarityOfTwoCases?caseID_1=animal0&caseID_2=animal1
            
        Parameters
        ----------
            caseID1 : The caseID of the first case
            caseID2 : The caseID of the second case
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeGlobalSimilarityOfTwoCases?' \
                    + 'caseID_1=' + caseID1 \
                    + '&caseID_2=' + caseID2

        print(final_url)

        response = requests.get(url=final_url)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = 'attributeID'
        df.columns = ['similarity']
        df = df.round(deci_precision)

        return df

    def computeEphemeralLocalSimilarity(
            self,
            caseID: str,
            ephemeralCaseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the local similarity (attribute similarities) for a given caseID against ephemeral case base.

            * Sample URL: ~/analytics/concepts/animal/casebases/case_base/amalgamationFunctions/rank_wt_all
            /computeEphemeralLocalSimilarity?caseID=animal0
            
        Parameters
        ----------
            caseID : The caseID
            ephemeralCaseIDs : List of caseIDs to be used as ephemeral casebase.
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeEphemeralLocalSimilarity?caseID=' + caseID

        # print( final_url)

        payload = ephemeralCaseIDs
        response = requests.post(url=final_url, json=payload)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df.transpose()

        return df

    def computeEphemeralGlobalSimilarity(
            self,
            caseID: str,
            ephemeralCaseIDs: List[str],
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the global similarity (attribute similarities) for a given caseID against ephemeral case base.

            * Sample URL: ~/analytics/concepts/animal/casebases/case_base/amalgamationFunctions/rank_wt_all
            /computeEphemeralGlobalSimilarity?caseID=animal0
            
        Parameters
        ----------
            caseID : The caseID
            ephemeralCaseIDs : List of caseIDs to be used as ephemeral casebase.
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeEphemeralGlobalSimilarity?caseID=' + caseID

        # print( final_url)

        payload = ephemeralCaseIDs
        response = requests.post(url=final_url, json=payload)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df.transpose()

        return df

    def computeLocalSimilarityWithAllCases(
            self,
            caseID: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the local similarity (attribute similarities) for a given caseID against the entire case base.

            * Sample URL: ~/analytics/concepts/animal/casebases/case_base/amalgamationFunctions/rank_wt_all
            /computeLocalSimilarityWithAllCases?caseID=animal0
            
        Parameters
        ----------
            caseID : The caseID
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeLocalSimilarityWithAllCases?caseID=' + caseID

        # print( final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df.transpose()

        return df

    def computeGlobalSimilarityWithAllCases(
            self,
            caseID: str,
            amalgamationFunctionID: str,
            conceptID: str = None,
            casebaseID: str = None,
            deci_precision: int = 3
    ) -> pd.DataFrame:

        """ 
        Compute the global similarity (attribute similarities including the weights) for
        a given caseID against the entire case base.

            * Sample URL: ~/analytics/concepts/animal/casebases/case_base/amalgamationFunctions/rank_wt_all
            /computeGlobalSimilarityWithAllCases?caseID=animal0
            
        Parameters
        ----------
            caseID : The caseID
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)
            casebaseID : Name of the casebase (default: self.__casebaseID)
            deci_precision : The numeric precision value for similarity (default: 3)

        Returns
        -------
            DataFrame : The rows are cases from the casebase with unique "caseID" and columns are the feature values.

        Note
        ----
            _unknown_ : is the placeholder for empty values
        """

        if conceptID is None:
            conceptID = self.__conceptID
        if casebaseID is None:
            casebaseID = self.__casebaseID

        final_url = self.__base_url \
                    + '/analytics' \
                    + '/concepts/' + conceptID \
                    + '/casebases/' + casebaseID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/computeGlobalSimilarityWithAllCases?caseID=' + caseID

        # print( final_url)

        response = requests.get(url=final_url)

        df = pd.DataFrame(response.json()).round(deci_precision)

        df = df.transpose()

        return df

    def getAttributeActiveSimilarityFunctions(
            self,
            amalgamationFunctionID: str,
            conceptID: str = None,
    ) -> pd.DataFrame:

        """ 
        Get attributes' active similarity functions for a given amalgamation function.

            * Sample URL: ~/analytics/concepts/animal/amalgamationFunctions/rank_wt_all
            /getAttributeActiveSimilarityFunctions
            
        Parameters
        ----------
            amalgamationFunctionID : Name of the amalgamation function
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            DataFrame : The rows are unique "attributeID" and columns are active 'localSimilarityFunctionID'.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/amalgamationFunctions/' + amalgamationFunctionID \
                    + '/getAttributeActiveSimilarityFunctions'

        # print( final_url)

        response = requests.get(url=final_url)

        response_json = response.json()

        df = pd.DataFrame(list(response_json.values()), index=response_json.keys())

        df.index.name = 'attributeID'
        df.columns = ['localSimilarityFunctionID']

        return df

    def getAllAttributeSimilarityFunctionIDs(
            self,
            conceptID: str = None,
    ) -> pd.DataFrame:

        """ 
        Get attributes' all similarity function IDs.

            * Sample URL: ~/analytics/concepts/animal/getAllAttributeSimilarityFunctionIDs
            
        Parameters
        ----------
            conceptID : Name of the concept (default: self.__conceptID)

        Returns
        -------
            DataFrame : The rows are the unique "attributeID" and columns are the 'localSimilarityFunctionIDs'.
        """

        if conceptID is None:
            conceptID = self.__conceptID

        final_url = self.__base_url \
                    + '/concepts/' + conceptID \
                    + '/getAllAttributeSimilarityFunctionIDs'

        # print( final_url)

        response = requests.get(url=final_url)

        dict_lsf = response.json()
        # print(dict_lsf)
        df = pd.DataFrame([(k, *v) for k, v in dict_lsf.items()])
        # python 3.6+ with f-strings
        df.columns = ['attributeID'] + [f'LSF_ID_{x}' for x in df.columns[1:]]

        return df
