#!/bin/bash

TARBALL_DIR=data/tarballs
JSON_DIR=data/json

echo "downloading 1 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-1-v1.tar.gz  -O $TARBALL_DIR/14-28-RAW-Solr-1-v1.tar.gz  
echo "downloading 2 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-2-v1.tar.gz  -O $TARBALL_DIR/14-28-RAW-Solr-2-v1.tar.gz 
echo "downloading 3 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-3a-v1.tar.gz -O $TARBALL_DIR/14-28-RAW-Solr-3a-v1.tar.gz
echo "downloading 4 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-3b-v1.tar.gz -O $TARBALL_DIR/14-28-RAW-Solr-3b-v1.tar.gz
echo "downloading 5 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-4-v1.tar.gz  -O $TARBALL_DIR/14-28-RAW-Solr-4-v1.tar.gz 
echo "downloading 6 of 6"
wget http://bulk.sunlightfoundation.com/openinternet/14-28-RAW-Solr-5-v1.tar.gz  -O $TARBALL_DIR/14-28-RAW-Solr-5-v1.tar.gz

tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-1-v1.tar.gz  -C $JSON_DIR/raw/
tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-2-v1.tar.gz  -C $JSON_DIR/raw/
tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-3a-v1.tar.gz -C $JSON_DIR/raw/
tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-3b-v1.tar.gz -C $JSON_DIR/raw/
tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-4-v1.tar.gz  -C $JSON_DIR/raw/
tar -xvzf $TARBALL_DIR/14-28-RAW-Solr-5-v1.tar.gz  -C $JSON_DIR/raw/
