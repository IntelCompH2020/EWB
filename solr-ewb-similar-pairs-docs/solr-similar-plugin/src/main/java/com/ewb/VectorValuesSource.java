package com.ewb;

import org.apache.lucene.analysis.payloads.PayloadHelper;
import org.apache.lucene.index.*;
import org.apache.lucene.search.DocIdSetIterator;
import org.apache.lucene.search.DoubleValues;
import org.apache.lucene.search.DoubleValuesSource;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.util.BytesRef;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.regex.*;
import java.util.Comparator;

/*
 * This class receives the query vector and computes its distance to the document vector by reading the vector values directly from the Lucene index. As distance metric, the Jensen-Shannon divergence is used.
 */
public class VectorValuesSource extends DoubleValuesSource {
    private final String field;

    private Terms terms; // Access to the terms in a specific field
    private TermsEnum te; // Iterator to step through terms to obtain frequency information
    private String[] limits;

    public VectorValuesSource(String field, String strVector) {
        /*
         * Document queries are assumed to be given as:
         * http://localhost:8983/solr/{your-corpus-collection-name}/query?fl=name,score,
         * vector&q={!vp f=doctpc_{your-model-name} vector="t0|43 t4|548 t5|6 t20|403"}
         * while topic queries as follows:
         * http://localhost:8983/solr/{your-model-collection-name}/query?fl=name,score,
         * vector&q={!vp f=betas
         * vector="high|43 research|548 development|6 neural_networks|403"}
         * Similar pairs of document queries are assumed to be given as:
         * http://localhost:8983/solr/{your-corpus-collection-name}/query?fl=name,score,
         * vector&q={!vs f=sim_{your-model-name} vector="20,50"}
         */
        this.field = field;
        this.limits = strVector.split(",");
    }

    public DoubleValues getValues(LeafReaderContext leafReaderContext, DoubleValues doubleValues) throws IOException {

        final LeafReader reader = leafReaderContext.reader();

        return new DoubleValues() {

            // Retrieves the payload value for each term in the document and calculates the
            // score based on vector lookup
            public double doubleValue() throws IOException {
                double score = 0;
                BytesRef text;
                String term = "";
                List<String> doc_id = new ArrayList<String>();
                List<Double> doc_sim = new ArrayList<Double>();
                while ((text = te.next()) != null) {
                    term = text.utf8ToString();
                    if (term.isEmpty()) {
                        continue;
                    }

                    // Get the semantic similarity
                    float payloadValue = 0f;
                    PostingsEnum postings = te.postings(null, PostingsEnum.ALL);
                    // And after we get TermsEnum instance te, we can compute the document vector by
                    // iterating all payload components (we will have as many components as topics
                    // the model has)
                    while (postings.nextDoc() != DocIdSetIterator.NO_MORE_DOCS) {
                        int freq = postings.freq();
                        while (freq-- > 0)
                            postings.nextPosition();

                        BytesRef payload = postings.getPayload();
                        payloadValue = PayloadHelper.decodeInt(payload.bytes, payload.offset);
                        doc_id.add(term);
                        doc_sim.add((double) payloadValue);
                    }
                }              

                double lowerLimit = Double.parseDouble(limits[0])/100;
                double upperLimit = Double.parseDouble(limits[1])/100;

                int low_index = -1;
                int up_index = -1;

                for (int i = 0; i < doc_id.size(); i++) {
                    double similarity = doc_sim.get(i);
                    
                    if (similarity <= upperLimit && low_index == -1) {
                        // Percentage of similarity is greater than or equal 
                        // to the lower percentage and the initial index has not yet been found.
                        low_index = i;
                    }
                    
                    if (similarity < lowerLimit) {
                        // Percentage of similarity is greater than the top percentage, 
                        // the final index is established and the cycle is broken.
                        up_index = i - 1;
                        break;
                    }
                }
                
                if (up_index == -1){
                    up_index = doc_id.size() - 1;
                }

                score = Double.parseDouble(low_index + "." + up_index);
                
                // Step 1: Filter the docSimilarity within the lower and upper limits
                /* 
                List<docSimilarity> filteredSimilarities = new ArrayList<>();
                for (int i = 0; i < doc_id.size(); i++) {
                    String id = doc_id.get(i);
                    double similarity = doc_sim.get(i);

                    if (similarity >= lowerLimit && similarity <= upperLimit) {
                        filteredSimilarities.add(new docSimilarity(id, similarity));
                    }
                }
                */
                // Step 2: Order filtered similarities in descendent order
                //Collections.sort(filteredSimilarities, new SimilarityComparator().reversed());
                /* 
                // Step 3: Create a new String with the filtered similarities
                List<String> output = new ArrayList<>();
                for (docSimilarity docSimilarity : filteredSimilarities) {
                    output.add(docSimilarity.getId() + "|" + docSimilarity.getSimilarity());
                }

                System.out.println(output);
                */

                return score;
            }

            // Advance to next document (for each document in the LeafReaderContext)
            public boolean advanceExact(int doc) throws IOException {
                terms = reader.getTermVector(doc, field);
                if (terms == null) {
                    return false;
                }
                te = terms.iterator();
                return true;
            }
        };
    }

    public boolean needsScores() {
        return true;
    }

    public DoubleValuesSource rewrite(IndexSearcher indexSearcher) throws IOException {
        return this;
    }

    public int hashCode() {
        return 0;
    }

    public boolean equals(Object o) {
        return false;
    }

    public String toString() {
        return "JS(" + field + ",doc)";
    }

    public boolean isCacheable(LeafReaderContext leafReaderContext) {
        return false;
    }
}
