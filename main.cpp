#include <vector>
#include <random>
#include <direct.h>

static const int c_numPoints = 128;
static const int c_numTrials = 1000;

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
                score = std::min(score, DistanceTorroidal(candidate, ret[comparisonIndex]));

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

    //fprintf(file, "\"%s\"\n", label);

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

        std::vector<float> blue = MBC1D(rng, c_numPoints);
        
        std::vector<float> regular(c_numPoints);
        float offset = dist(rng);
        for (int i = 0; i < c_numPoints; ++i)
            regular[i] = Fract(offset + (float(i) + 0.5f) / float(c_numPoints));

        std::vector<float> stratified(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
            stratified[i] = (float(i) + dist(rng)) / float(c_numPoints);

        std::vector<float> white(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
            white[i] = dist(rng);

        std::vector<float> goldenRatio(c_numPoints);
        goldenRatio[0] = dist(rng);
        for (int i = 1; i < c_numPoints; ++i)
            goldenRatio[i] = Fract(goldenRatio[i - 1] + c_goldenRatioConjugate);

        std::vector<float> antithetic(c_numPoints);
        for (int i = 0; i < c_numPoints; ++i)
        {
            if (i % 2 == 0)
                antithetic[i] = dist(rng);
            else
                antithetic[i] = 1.0f - antithetic[i - 1];
        }

        WriteResults(blue, "blue", trial);
        WriteResults(regular, "regular", trial);
        WriteResults(stratified, "stratified", trial);
        WriteResults(white, "white", trial);
        WriteResults(goldenRatio, "goldenratio", trial);
        WriteResults(antithetic, "antithetic", trial);
    }
    printf("\n\n");
}

/*

TODO:
- sort by x, subtract to get distances, DFT, make graphs of DFT (with python)
 - doing N trials to average the DFT results?
 - probably should also make a numberline of samples (python?).

*/