use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use clap::{Parser};

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use rdf::node::Node;

use rdf::reader::turtle_parser::TurtleParser;
use rdf::reader::rdf_parser::RdfParser;
use rdf::uri::Uri;

fn long_list_to_short_str(lst: &Vec<f64>) -> String {
    let lst_len: usize = lst.len();
    if lst_len <= 7 {
        return format!("{:?}", lst);
    } else {
        return format!("[{}, {}, ..., {}, ..., {}, {}]",
                       lst[0], lst[1], lst[lst_len/2], lst[lst_len-2], lst[lst_len-1]);
    }
}

/// Merges two sorted lists.
/// The resulting iterator contains no duplicates, i.e. each value only once.
fn merge(sorted_list_1: Vec<f64>, sorted_list_2: Vec<f64>)
    -> impl std::iter::Iterator<Item=(f64, usize, usize)> {
    let len_sorted_list_1 = sorted_list_1.len();
    let len_sorted_list_2 = sorted_list_2.len();

    let mut index1: usize = 0;
    let mut index2: usize = 0;
    let mut x: f64 = f64::NAN;
    // cf. https://stackoverflow.com/questions/16421033/lazy-sequence-generation-in-rust:
    return std::iter::from_fn(move || {
        if index1 < len_sorted_list_1 || index2 < len_sorted_list_2 { // `while` in Python
            if index1 == len_sorted_list_1 {
                x = sorted_list_2[index2];
            } else if index2 == len_sorted_list_2 {
                x = sorted_list_1[index1];
            } else {
                x = sorted_list_1[index1].min(sorted_list_2[index2]);
            }

            while index1 < len_sorted_list_1 && sorted_list_1[index1] == x {
                index1 += 1;
            }
            while index2 < len_sorted_list_2 && sorted_list_2[index2] == x {
                index2 += 1;
            }

            return Some((x, index1, index2)); // `yield` in Python
        }
        return None;
    });
}

/// Computes the KS similarity between two given bags of numerical values,
/// one already sorted bag and one unsorted bag, efficiently.
///
/// Attention:
/// Throws a `ZeroDivisionError` when either of the given bags/lists
/// is empty!
fn ks(sorted_bag: Vec<f64>, mut unsorted_bag: Vec<f64>) -> f64 {
    unsorted_bag.sort_by(|a, b| a.partial_cmp(b).unwrap());
    // see https://users.rust-lang.org/t/how-to-sort-a-vec-of-floats/2838
    // because the trait `Ord` is not implemented for `f64`

    let one_over_len_sorted_bag: f64 = 1.0 / (sorted_bag.len() as f64);
    let one_over_len_unsorted_bag: f64 = 1.0 / (unsorted_bag.len() as f64);

    let mut max_difference: f64 = 0.0;

    for (x, index1, index2)
        in merge(sorted_bag, unsorted_bag) {
        max_difference = max_difference.max(
                             ((index1 as f64) * one_over_len_sorted_bag -
                                 (index2 as f64) * one_over_len_unsorted_bag).abs());
    }

    return max_difference;
}

/// Takes the extension of a numeric column as input
/// and tries to match it to a DBpedia property and corresponding class.
#[derive(Parser, Debug)]
#[clap(about, version, author)]
struct Args {
    /// Path (or URL) to a .ttl (turtle) file of
    /// DBpedia resources mapped to their types (22-rdf-syntax-ns#type).
    /// Download an unzip
    /// downloads.dbpedia.org/2016-04/core-i18n/en/instance_types_en.ttl.bz2
    /// for example.
    #[clap(long, parse(from_os_str))]
    types: PathBuf,

    /// Path (or URL) to a .ttl (turtle) file of
    /// DBpedia resources mapped to their properties and values.
    /// Download an unzip
    /// downloads.dbpedia.org/2016-04/core-i18n/en/infobox_properties_mapped_en.ttl.bz2
    /// for example.
    #[clap(long, parse(from_os_str))]
    properties: PathBuf,

    /// The number of (DBpedia type, DBpedia property) pairs to output.
    /// Default value: 100
    #[clap(short, default_value_t=100)]
    k: usize,

    /// A bag of numerical values.
    bag: Vec<f64>,

    /// Path to a CSV file. The n-th column specified with the
    /// --csv-column argument will be used as input to this script.
    /// It has to be a numerical column containing integer or float values!
    #[clap(long, parse(from_os_str))]
    csv_file: Option<PathBuf>,

    /// The separator symbol used in the CSV file specified by the
    /// --csv-file argument. (Default: TAB)
    #[clap(long)]
    csv_separator: Option<String>,

    /// Which column to use as input in the CSV file given by
    /// the --csv-file argument. The first column has index 0.
    /// (Default: 0)
    #[clap(long)]
    csv_column: Option<usize>
}

fn main() {
    let args = Args::parse();

    // Maps each DBpedia resource to its DBpedia type:
    let mut dbpedia_resource_to_type: HashMap<String, String> = HashMap::new();

    // Maps each pair of a DBpedia type and numeric DBpedia property
    //   to the list of values taken by all DBpedia resources that are an
    //   instance of that type:
    let mut dbpedia_type_and_property_to_extension
        : HashMap<(String, String), Vec<f64>> = HashMap::new();

    println!();
    println!("[1/6] Parsing --types .ttl file...");

    // Parse the .ttl file passed as --types:
    // cf. https://docs.rs/rdf/latest/rdf/:
    let types_ttl_content = fs::read_to_string(args.types)
        .expect("Reading --types .ttl file failed!");
    let mut reader =
        TurtleParser::from_string(types_ttl_content);
    let types_graph = reader.decode().expect("Parsing --types .ttl file failed!");

    println!("[2/6] Parsing --properties .ttl file...");

    // Parse the .ttl file passed as --properties:
    let properties_ttl_content = fs::read_to_string(args.properties)
        .expect("Reading --properties .ttl file failed!");
    let mut reader =
        TurtleParser::from_string(properties_ttl_content);
    let properties_graph = reader.decode().expect("Parsing --properties .ttl file failed!");

    println!("[3/6] Populating dictionary with parsed --types .ttl file...");

    // Iterate through the (subject, predicate, object) triples
    //   and populate dbpedia_resource_to_type:
    for triple in types_graph.triples_iter() {
        if !node_to_string(triple.predicate()).contains("22-rdf-syntax-ns#type") {
            continue;
        }

        let _resource = node_to_string(triple.subject())
            .strip_prefix("http://dbpedia.org/resource/");

        let _type = node_to_string(triple.object())
            .strip_prefix("http://dbpedia.org/ontology/");

        if _type.contains("/") {
            continue;  // skip Things: (http://)www.w3.org/2002/07/owl#Thing
        }

        dbpedia_resource_to_type[_resource] = _type
    }

    println!("[4/6] Populating dictionary with parsed --properties .ttl file...");

    // Iterate through the (subject, predicate, object) triples
    //   and populate dbpedia_type_and_property_to_extension:
    for triple in properties_graph.triples_iter() {
        // ToDo: possibly more advanced parsing:
        if let Some(_value) = triple.object().literal.parse::<f64>() {

            let _resource = node_to_string(triple.subject())
                .strip_prefix("http://dbpedia.org/resource/");

            let _property = node_to_string(triple.predicate())
                .strip_prefix("http://dbpedia.org/property/");

            if let Some(_type) = dbpedia_resource_to_type.get(_resource) {
                dbpedia_type_and_property_to_extension.entry((_type.clone(), _property))
                    .or_insert_with(|| Vec::new())
                    .push(_value);
            }
        }
    }

    // The input bag to compare against all DBpedia numerical bags:
    let mut bag: Vec<f64>;
    if let Some(csv_file) = args.csv_file {
        // cf. https://doc.rust-lang.org/rust-by-example/std_misc/file/read_lines.html:
        let lines = read_lines(csv_file)
            .expect("cannot read given CSV file!");
        for line in lines {
            if let Ok(line) = line {
                if line.trim() == "" || line.get(..1) == Some("#") {
                    continue;
                } else {
                    if let Some(Ok(number)) = line
                        .split(&args.csv_separator.unwrap_or("\t".to_string()))
                        .nth(args.csv_column.unwrap_or(0))
                        .map(|s| s.trim().parse::<f64>()) {
                        bag.push(number);
                    }
                }
            }
        }
    } else {
        bag = args.bag;
    }
    println!("[INFO] Unsorted input bag = {}", long_list_to_short_str(&bag));
    bag.sort_by(|a, b| a.partial_cmp(b).unwrap());

    println!("[5/6] Computing KS scores...");

    // Maps each pair of a DBpedia type and numeric DBpedia property
    //   to the metric returned by the KS (Kolmogorov–Smirnov) test
    //   on the list of values taken by all DBpedia resources that are an
    //   instance of that type and the input list of numeric values:
    let dbpedia_type_and_property_to_ks_test: HashMap<(String, String), f64> =
        HashMap::from_iter(
            dbpedia_type_and_property_to_extension
                    .into_iter()
                    .map(|(key, lst)|
                        (key, ks(bag, lst)))
        );

    println!("[6/6] Sorting results by KS score...");

    let mut dbpedia_type_and_property_to_ks_test_sorted
        : Vec<((String, String), f64)> =
        dbpedia_type_and_property_to_ks_test.into_iter().collect();
    dbpedia_type_and_property_to_ks_test_sorted
        .sort_by(|a, b| a.partial_cmp(b).unwrap());
    // smaller KS values == more similar

    println!();
    println!("KS Score - DBpedia type - DBpedia property - Matched list");
    println!();
    for i in 0..args.k.min(
                          dbpedia_type_and_property_to_ks_test_sorted[0..args.k].len()) {
        let el: ((String, String), f64) = dbpedia_type_and_property_to_ks_test_sorted[i];
        let dbpedia_type = el.0.0;
        let dbpedia_property = el.0.1;
        let ks_test_score = el.1;
        let matched_list =
            dbpedia_type_and_property_to_extension[
                &(dbpedia_type, dbpedia_property)];

        println!("{} - {} -
                {} - {}",
                 ks_test_score, dbpedia_type, dbpedia_property,
                 long_list_to_short_str(&matched_list)
        );
    }
}

fn node_to_string(node: &Node) -> &String {
    match node {
        Node::UriNode { uri } => uri.to_string(),
        Node::LiteralNode { literal, data_type, language }
            => &literal,
        Node::BlankNode { id } => &id,
    }
}

// Source: https://doc.rust-lang.org/rust-by-example/std_misc/file/read_lines.html
//
// The output is wrapped in a Result to allow matching on errors
// Returns an Iterator to the Reader of the lines of the file.
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
    where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}
