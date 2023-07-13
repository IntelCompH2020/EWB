package com.ewb;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.junit.Test;

public class DistanceTest {
    @Test
    public void testJensenShannonDivergence1() {
        System.out.println("Starting test 1...");
        double[] p = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
        double[] q = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

        double score = 0;
        Distance d = new Distance();
        score = d.JensenShannonDivergence(p, q);

        // assertTrue(MathEx.KullbackLeiblerDivergence(prob, p) < 0.05);
        System.out.println(score);

    }

    @Test
    public void testJensenShannonDivergence2() {
        System.out.println("Starting test 2...");
        double[] p = { 1, 2, 3, 4, 5, 6, 7 };
        double[] q = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

        double score = 0;
        Distance d = new Distance();
        try {
            score = d.JensenShannonDivergence(p, q);
            System.out.println(score);
        } catch (Exception e) {
            System.out.println(e);
        }
    }

    @Test
    public void testJensenShannonDivergence3() {
        System.out.println("Starting test 3...");
        double[] p = { 0, 105, 0, 0, 0, 0, 471, 0, 15, 0, 0, 120, 0, 0, 71, 0, 0, 0, 0, 0, 218, 0, 0, 0, 0 };
        double[] q = { 0, 4, 0, 1, 0, 4, 0, 4, 0, 1, 0, 4, 0, 4, 0, 1, 0, 4, 5, 3, 4, 3, 2, 0, 0 };

        double score = 0;
        Distance d = new Distance();
        score = d.JensenShannonDivergence(p, q);

        // assertTrue(MathEx.KullbackLeiblerDivergence(prob, p) < 0.05);
        System.out.println(score);

    }

    @Test
    public void testFirstApproach() {
        System.out.println("Starting test 4...");
        String query_vector = "20,50";
        String doc_vector = "218417|0.68 831809|0.33 314692|0.43 717081|0.12";

        String[] limits = query_vector.split(",");
    
        List<String> doc_id = new ArrayList<String>();
        List<Double> doc_sim = new ArrayList<Double>();

        for (String comp : doc_vector.split(" ")) {
            String tpc_id = comp.split("\\|")[0];
            doc_id.add(tpc_id);
            doc_sim.add(Double.parseDouble(comp.split("\\|")[1]));
        }
        System.out.println(doc_id);
        System.out.println(doc_sim);

        double lowerLimit = Double.parseDouble(limits[0])/100;
        double upperLimit = Double.parseDouble(limits[1])/100;

        System.out.println(lowerLimit);
        System.out.println(upperLimit);

        // Step 1: Filter the docSimilarity within the lower and upper limits
        List<docSimilarity> filteredSimilarities = new ArrayList<>();
        for (int i = 0; i < doc_id.size(); i++) {
            String id = doc_id.get(i);
            double similarity = doc_sim.get(i);

            if (similarity >= lowerLimit && similarity <= upperLimit) {
                filteredSimilarities.add(new docSimilarity(id, similarity));
            }
        }
        for (docSimilarity d : filteredSimilarities) {
            System.out.println("Id: "+ d.getId()+ ", Similarity: " +  d.getSimilarity());
        }
        System.out.println("Now, we order the list");
        // Step 2: Order filtered similarities in descendent order
        Collections.sort(filteredSimilarities, new SimilarityComparator().reversed());

        for (docSimilarity d : filteredSimilarities) {
            System.out.println("Id: "+ d.getId()+ ", Similarity: " +  d.getSimilarity());
        }

        System.out.println(filteredSimilarities);
    }

    @Test
    public void testSecondApproach() {
        System.out.println("Starting test 5...");
        double score = 0.0;
        String query_vector = "20,50";
        String doc_vector = "218417|0.68 314692|0.43 831809|0.33 717081|0.12";

        String[] limits = query_vector.split(",");
    
        List<String> doc_id = new ArrayList<String>();
        List<Double> doc_sim = new ArrayList<Double>();

        for (String comp : doc_vector.split(" ")) {
            String tpc_id = comp.split("\\|")[0];
            doc_id.add(tpc_id);
            doc_sim.add(Double.parseDouble(comp.split("\\|")[1]));
        }

        double lowerLimit = Double.parseDouble(limits[0])/100;
        double upperLimit = Double.parseDouble(limits[1])/100;
        
        System.out.println(lowerLimit);
        System.out.println(upperLimit);

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
        System.out.println(score);
    }
}
