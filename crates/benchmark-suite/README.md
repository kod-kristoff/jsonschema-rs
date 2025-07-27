# Benchmark Suite

A benchmarking suite for comparing different Rust JSON Schema implementations.

## Implementations

- `jsonschema` (latest version in this repo)
- [valico](https://crates.io/crates/valico) (v4.0.0)
- [jsonschema-valid](https://crates.io/crates/jsonschema-valid) (v0.5.2)
- [boon](https://crates.io/crates/boon) (v0.6.0)

## Usage

To run the benchmarks:

```console
$ cargo bench
```

## Overview

| Benchmark     | Description                                    | Schema Size | Instance Size |
|----------|------------------------------------------------|-------------|---------------|
| OpenAPI  | Zuora API validated against OpenAPI 3.0 schema | 18 KB       | 4.5 MB        |
| Swagger  | Kubernetes API (v1.10.0) with Swagger schema   | 25 KB       | 3.0 MB        |
| GeoJSON  | Canadian border in GeoJSON format              | 4.8 KB      | 2.1 MB        |
| CITM     | Concert data catalog with inferred schema      | 2.3 KB      | 501 KB        |
| Fast     | From fastjsonschema benchmarks (valid/invalid) | 595 B       | 55 B / 60 B   |

Sources:
- OpenAPI: [Zuora](https://github.com/APIs-guru/openapi-directory/blob/1afd351ddf50e050acdb52937a819ef1927f417a/APIs/zuora.com/2021-04-23/openapi.yaml), [Schema](https://spec.openapis.org/oas/3.0/schema/2021-09-28)
- Swagger: [Kubernetes](https://raw.githubusercontent.com/APIs-guru/openapi-directory/master/APIs/kubernetes.io/v1.10.0/swagger.yaml), [Schema](https://github.com/OAI/OpenAPI-Specification/blob/main/_archive_/schemas/v2.0/schema.json)
- GeoJSON: [Schema](https://geojson.org/schema/FeatureCollection.json)
- CITM: Schema inferred via [infers-jsonschema](https://github.com/Stranger6667/infers-jsonschema)
- Fast: [fastjsonschema benchmarks](https://github.com/horejsek/python-fastjsonschema/blob/master/performance.py#L15)

## Results

### Comparison with Other Libraries

| Benchmark     | jsonschema_valid | valico        | boon          | jsonschema (validate) |
|---------------|------------------|---------------|---------------|------------------------|
| OpenAPI       | -                | -             | 6.60 ms (**x3.17**) | 2.0813 ms            |
| Swagger       | -                | 114.26 ms (**x51.90**)   | 10.06 ms (**x4.57**)     | 2.2021 ms            |
| GeoJSON       | 19.56 ms (**x23.37**)      | 299.53 ms (**x358.00**)   | 16.59 ms (**x19.82**)  | 836.93 µs            |
| CITM Catalog  | 2.84 ms (**x7.40**)        | 28.30 ms (**x73.74**)    | 1.11 ms (**x2.89**)     | 383.98 µs            |
| Fast (Valid)  | 1.11 µs (**x14.67**)       | 3.78 µs (**x49.94**)     | 332.39 ns (**x4.39**)   | 75.748 ns            |
| Fast (Invalid)| 247.88 ns (**x4.67**)      | 3.82 µs (**x71.93**)     | 383.79 ns (**x7.22**)   | 53.176 ns            |

### jsonschema Performance: `validate` vs `is_valid`

| Benchmark     | validate   | is_valid   | Speedup |
|---------------|------------|------------|---------|
| OpenAPI       | 2.0813 ms  | 2.0612 ms  | **1.01x**   |
| Swagger       | 2.2021 ms  | 2.0729 ms  | **1.06x**   |
| GeoJSON       | 836.93 µs  | 796.28 µs  | **1.05x**   |
| CITM Catalog  | 383.98 µs  | 313.13 µs  | **1.23x**   |
| Fast (Valid)  | 75.748 ns  | 53.642 ns  | **1.41x**   |
| Fast (Invalid)| 53.176 ns  | 3.4919 ns  | **15.23x**  |

Notes:

1. `jsonschema_valid` and `valico` do not handle valid path instances matching the `^\\/` regex.

2. `jsonschema_valid` fails to resolve local references (e.g. `#/definitions/definitions`).

You can find benchmark code in [benches/](benches/), Rust version is `1.82`.

## Contributing

Contributions to improve, expand, or optimize the benchmark suite are welcome. This includes adding new benchmarks, ensuring fair representation of real-world use cases, and optimizing the configuration and usage of benchmarked libraries. Such efforts are highly appreciated as they ensure accurate and meaningful performance comparisons.

