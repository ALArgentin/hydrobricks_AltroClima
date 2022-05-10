#ifndef HYDROBRICKS_TIME_SERIES_H
#define HYDROBRICKS_TIME_SERIES_H

#include "Includes.h"
#include "TimeSeriesData.h"

class TimeSeries : public wxObject {
  public:
    explicit TimeSeries(VariableType type);

    ~TimeSeries() override = default;

    virtual bool SetCursorToDate(const wxDateTime &dateTime) = 0;

    virtual bool AdvanceOneTimeStep() = 0;

    virtual bool IsDistributed() = 0;

    virtual wxDateTime GetStart() = 0;

    virtual wxDateTime GetEnd() = 0;

    virtual TimeSeriesData* GetDataPointer(int unitId) = 0;

    VariableType GetVariableType() {
        return m_type;
    }

  protected:
    VariableType m_type;

  private:
};

#endif  // HYDROBRICKS_TIME_SERIES_H
