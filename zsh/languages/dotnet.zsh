_dotnet_cov() {
  dotnet test --collect:"XPlat Code Coverage"
  coverage_file=$(find . -type f -name "coverage.cobertura.xml" -print0 | xargs -0 ls -t | head -n1)
  reportgenerator -reports:$coverage_file -targetdir:coverage-report -reporttypes:Html
  open coverage-report/index.html
}

alias dotnet-cov="_dotnet_cov"
