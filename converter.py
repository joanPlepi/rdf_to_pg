# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 13:25:40 2018

@author: Joan Plepi
"""

from pygraphml import GraphMLParser
from pygraphml import Graph
from rdflib import graph

class Converter():
    def __init__(self, filename):
        """Initializing the class variables.
        
        Keyword arguments:
        file_name -- the name of the file which we want to convert.
        nodes -- dictionary which uses as a key an id and value is subject or object.
        value_key_node -- dictionary where the key and value of nodes dictionary is reversed.
        labels -- dictionary where key is the subject and value it's label.
        relations -- list where every element saves a triple subject predicate object.
        nodes_prop -- every element is a list with properties of a subject. 
        """
        self.file_name = filename
        self.nodes = {}
        self.value_key_nodes = {}
        self.labels = {}
        self.relations = []
        self.nodes_prop = {}
    
    def __read_file(self):
        """Reads the given file.
        
        Uses Graph class from rdflib library to read the file. 
        A SPARQL query is used to get all the data from the file. 
        Returns the results of the query after it is executed.
        """
        g = graph.Graph()
        
        extension = self.file_name.split(".")
        extension = extension[-1]
        g.parse(self.file_name, format=extension)
        
        query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>     
            SELECT ?sub ?pred ?obj
            WHERE {
                 ?sub ?pred ?obj.
            }
            """
                
        qres = g.query(query)
        return qres
    
    def __write_graphML(self):
        """Writes the .graphml file.
        
        Uses class Graph from pygraphml library to create the graph. 
        Also it uses class GraphMLParser from pygraphml library to write the file.
        """
        gr = Graph()
        
        # Adding nodes in the graph with properties.
        for sub in self.nodes_prop.keys():
            n = gr.add_node(sub)
            for pair_prop in self.nodes_prop[sub]:
                n[pair_prop[0]] = pair_prop[1]
                
        # Adding nodes in the graph without properties.
        for node in self.nodes.values():
            if node not in self.nodes_prop.keys():
                gr.add_node(node)
        
        # Checking the relations between nodes and creating respective edges.
        for relation in self.relations:
            source = self.nodes[relation[0]]
            target = self.nodes[relation[2]]
            edge = gr.add_edge_by_label(source, target)
            edge.set_directed(True)
            edge['model'] = relation[1]
            
        # Writting the file. 
        parser = GraphMLParser()
        file_name = self.file_name.split(".")
        file_name = file_name[0]
        
        parser.write(gr, file_name + ".graphml")
        print("File  " + file_name + ".graphml is succesfully written")
        
        
        
    def execute(self):
        """Extracts information from the SPARQL query results.
        
        Uses the class methods __read_file() and __write_file().
        Iterates through all the rows returned by the result of query.
        It does string manipulation to get the corresponding subject predicate and object.
        Stores and organizes the information in the data structures declared above. 
        The data structures are used from __write_file() method to create the output graph.
        """
        
        # Getting the results from __read_file() method
        qres = self.__read_file()
        
        id_node = 0 # initializing id_node
        i = 0
        # Iterating through all the rows of query results. 
        for row in qres:         
            triple = row
            
            # Reading subject
            sub = triple[0].split("/")
            sub = sub[-1]
            
            # Checking if we have already save subject in the dictionary. 
            if sub not in self.nodes.values():
                self.nodes[id_node] = sub
                self.value_key_nodes[sub] = id_node
                id_node = id_node + 1
                
            # Manipulating the predicate. 
            # Label predicates are checked here.
            if triple[1].find("#label") != -1:
                       obj = triple[2]
                       self.labels[sub] = obj           
            else:
                # Type predicates are checked here.
                if triple[1].find("#type") != -1:
                     pred = "type"
                else:
                    # Get the other predicates.
                    pred = triple[1].split("/")
                    pred = pred[-1]
                
                # Manipulating the object.
                obj = triple[2]   
                
                # Checks if object is an IRI or literal.
                if "http" in obj:
                    obj =  triple[2].split("/")
                    obj = obj[-1]
                    
                    if obj not in self.nodes.values():
                        # If object is an IRI we save the relation with the subject.
                        self.nodes[id_node] = obj
                        self.value_key_nodes[obj] = id_node
                        id_node = id_node + 1
                    self.relations.append((self.value_key_nodes[sub] , pred, self.value_key_nodes[obj]))

                else:
                    # If object is a literal, we add it as a property to the subject. 
                    if sub not in self.nodes_prop:
                        self.nodes_prop[sub] = []
                    self.nodes_prop[sub].append((pred, obj))
                    
        # Calling the method to write the graph.     
        self.__write_graphML()           
        
        
       
        