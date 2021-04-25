#include <vector>
#include <random>
#include <direct.h>

static const int c_numPoints = 256;
static const int c_numTrials = 10;

static const float c_goldenRatioConjugate = 0.61803398875f;

float DistanceTorroidal(float A, float B)
{
    float dist = abs(B - A);
    if (dist > 0.5f)
        dist = 1.0f - dist;
    return dist;
}

std::vector<float> MBC1D(std::mt19937& rng, int numPoints)
{
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);

    std::vector<float> ret(numPoints, 0);

    for (int pointIndex = 0; pointIndex < numPoints; ++pointIndex)
    {
        float bestScore = -FLT_MAX;
        float bestCandidate = 0.0f;
        for (int candidateIndex = 0; candidateIndex < pointIndex + 1; ++candidateIndex)
        {
            float score = FLT_MAX;
            float candidate = dist(rng);

            for (int comparisonIndex = 0; comparisonIndex < pointIndex; ++comparisonIndex)
                score = std::min(score, DistanceTorroidal(candidate, ret[pointIndex]));

            if (score > bestScore)
            {
                bestCandidate = candidate;
                bestScore = score;
            }
        }
        ret[pointIndex] = bestCandidate;
    }

    return ret;
}

float Fract(float f)
{
    return f - std::floor(f);
}

void WriteResults(const std::vector<float>& results, const char* label, int trial)
{
    std::vector<float> resultsSorted = results;
    std::sort(resultsSorted.begin(), resultsSorted.end());

    char fileName[1024];
    sprintf_s(fileName, "out/%s_%i.csv", label, trial);
    FILE* file = nullptr;
    fopen_s(&file, fileName, "wt");

    fprintf(file, "\"%s\"\n", label);

    for (float f : resultsSorted)
        fprintf(file, "\"%f\"\n", f);

    fclose(file);
}

int main(int argc, char** argv)
{
    std::mt19937 rng;
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);

    _mkdir("out");
    
    for (int trial = 0; trial < c_numTrials; ++trial)
    {
        printf("\rtrial: %i/%i", trial+1, c_numTrials);

        std::vector<float> bn = MBC1D(rng, c_numPoints);
        
        std::vector<float> uniform(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
            uniform[i] = (float(i) + 0.5f) / float(c_numPoints);

        std::vector<float> stratified(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
            stratified[i] = (float(i) + dist(rng)) / float(c_numPoints);

        std::vector<float> white(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
            white[i] = dist(rng);

        std::vector<float> gr(c_numPoints);
        gr[0] = dist(rng);
        for (int i = 1; i < c_numPoints; ++i)
            gr[i] = Fract(gr[i - 1] + c_goldenRatioConjugate);

        std::vector<float> av(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
        {
            if (i % 2 == 0)
                av[i] = dist(rng);
            else
                av[i] = 1.0f - av[i - 1];
        }

        WriteResults(bn, "bn", trial);
        WriteResults(uniform, "uniform", trial);
        WriteResults(stratified, "stratified", trial);
        WriteResults(white, "white", trial);
        WriteResults(gr, "gr", trial);
        WriteResults(av, "av", trial);
    }
    printf("\n\n");
}

/*

TODO:
- sort by x, subtract to get distances, DFT, make graphs of DFT (with python)
 - doing N trials to average the DFT results?
 - probably should also make a numberline of samples (python?).

*/